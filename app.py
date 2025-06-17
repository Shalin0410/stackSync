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

    # Create a temp script file inside /tmp
    script_id = str(uuid.uuid4())
    script_path = f"/tmp/{script_id}.py"

    try:
        with open(script_path, "w") as f:
            f.write(script)

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
            }), 500

        # Expect JSON return in stdout's last line
        try:
            lines = stdout.splitlines()
            output_json = json.loads(lines[-1])
            printed = "\n".join(lines[:-1])
        except Exception as e:
            return jsonify({
                "error": "Script did not return valid JSON from main()",
                "stdout": stdout
            }), 400

        return jsonify({
            "result": output_json,
            "stdout": printed
        })

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Script execution timed out"}), 408
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
