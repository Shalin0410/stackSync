from flask import Flask, request, jsonify
import subprocess
import os
import uuid
import json

app = Flask(__name__)

NSJAIL_PATH = "/usr/local/bin/nsjail"
NSJAIL_CFG = "/app/nsjail.cfg"
PYTHON_BIN = "/usr/bin/python3"

@app.route("/execute", methods=["POST"])
def execute_script():
    data = request.get_json()

    if not data or "script" not in data:
        return jsonify({"error": "Missing 'script' field in JSON"}), 400

    script = data["script"]
    
    # Add wrapper to ensure main() function returns JSON
    wrapper_script = script + """

if __name__ == "__main__":
    import json
    try:
        result = main()
        print(json.dumps(result))
    except NameError as e:
        if "main" in str(e):
            print(json.dumps({"error": "Function 'main' is not defined"}))
        else:
            print(json.dumps({"error": str(e)}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
"""

    # Create temp script file
    script_id = str(uuid.uuid4())
    script_path = f"/tmp/{script_id}.py"

    try:
        with open(script_path, "w") as f:
            f.write(wrapper_script)

        # Run in nsjail sandbox
        result = subprocess.run(
            [NSJAIL_PATH, "--config", NSJAIL_CFG, "--", PYTHON_BIN, script_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            return jsonify({"error": "Script execution failed", "stderr": stderr}), 400

        try:
            lines = stdout.splitlines()
            if not lines:
                return jsonify({"error": "Script produced no output"}), 400
                
            # Parse JSON result from last line
            output_json = json.loads(lines[-1])
            
            # Get printed output from all but last line
            printed = "\n".join(lines[:-1]) if len(lines) > 1 else ""
            
            # Check for error in execution
            if isinstance(output_json, dict) and "error" in output_json:
                return jsonify({
                    "error": "Script execution failed",
                    "message": output_json["error"],
                    "stdout": printed
                }), 400
                
            # Return result in required format
            return jsonify({"result": output_json, "stdout": printed})
                
        except json.JSONDecodeError:
            return jsonify({
                "error": "Script did not return valid JSON from main()",
                "stdout": stdout
            }), 400

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Script execution timed out"}), 408
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)