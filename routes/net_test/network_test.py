from flask import jsonify, Blueprint
import speedtest

net_test_bp = Blueprint('net_test', __name__)


@net_test_bp.route('/speedtest', methods=['GET'])
def run_speedtest():
    try:
        # Create a Speedtest object
        s = speedtest.Speedtest()
        
        # Get the list of available servers and find the best one
        servers = s.get_servers()
        s.get_best_server()
     
        # Run the speed test
        download_speed = s.download(threads=None) / 1024 / 1024  # Convert bits to megabits
        upload_speed = s.upload(threads=None, pre_allocate=False) / 1024 / 1024  # Convert bits to megabits
        
        results_dict = s.results.dict()
        
        response = {
            "download_speed": round(download_speed, 2),
            "upload_speed": round(upload_speed, 2),
            "server": {
                "url": results_dict["server"]["url"],
                "latency": results_dict["server"]["latency"],
                "name": results_dict["server"]["name"],
                "country": results_dict["server"]["country"],
                "sponsor": results_dict["server"]["sponsor"]
            }
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  

