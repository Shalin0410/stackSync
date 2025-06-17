from flask import Flask, request, jsonify
import tempfile
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
    
    # Modify the script to ensure it has a main() function that returns JSON
    wrapper_script = script + """

# Wrapper to ensure main() function returns JSON
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

    # Create a temp script file inside /tmp
    script_id = str(uuid.uuid4())
    script_path = f"/tmp/{script_id}.py"

    try:
        with open(script_path, "w") as f:
            f.write(wrapper_script)

        # Run nsjail with the script
        result = subprocess.run(
            [
                NSJAIL_PATH,
                "--config", NSJAIL_CFG,
                "--", PYTHON_BIN, script_path
            ],
            capture_output=True,
            text=True,
            timeout=10  # safety timeout
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            return jsonify({
                "error": "Script execution failed",
                "stderr": stderr
            }), 400

        # Expect JSON return in stdout's last line
        try:
            lines = stdout.splitlines()
            if not lines:
                return jsonify({"error": "Script produced no output"}), 400
                
            # The last line should be our JSON result
            output_json = json.loads(lines[-1])
            
            # Everything before the last line is printed output
            printed = "\n".join(lines[:-1]) if len(lines) > 1 else ""
            
            # Check if there was an error in the script execution
            if isinstance(output_json, dict) and "error" in output_json:
                return jsonify({
                    "error": "Script execution failed",
                    "message": output_json["error"],
                    "stdout": printed
                }), 400
                
            # Return exactly the format specified in the requirements
            return jsonify({
                "result": output_json,
                "stdout": printed
            })
                
        except json.JSONDecodeError:
            return jsonify({
                "error": "Script did not return valid JSON from main()",
                "stdout": stdout,
                "stderr": stderr
            }), 400

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Script execution timed out"}), 408
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    finally:
        # Clean up the temporary script file
        if os.path.exists(script_path):
            os.remove(script_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)