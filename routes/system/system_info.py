import psutil
from flask import jsonify, Blueprint

system_bp = Blueprint('system', __name__)

# Gets system information RAM - DISK SPACE - NETWORK STATS - CPU CORES
@system_bp.route('/system_info',  methods=['GET'])
def system_info():
    result = {'success': False, 'error': None, 'data': None}
    
    try:
        system_info = {}

        # CPU information
        cpu_info = psutil.cpu_count(logical=True)
        system_info['CPU Cores'] = cpu_info

        # Logged users
        logged_in_users = psutil.users()
        usernames = [user.name for user in logged_in_users]
        system_info['users'] = usernames

        # RAM information
        mem_info = psutil.virtual_memory()

        total_ram = mem_info.total / (1024 ** 3)  # Convert bytes to gigabytes
        available_ram = mem_info.available / (1024 ** 3)  
        percentage_ram = mem_info.percent 
        used_ram = mem_info.used / (1024 ** 3)  
        system_info['RAM'] = {
            'total': round(total_ram, 2),
            'available': round(available_ram, 2),
            'percentage_used': round(percentage_ram, 2),
            'used': round(used_ram, 2)
        }

        # Disk information
        disk_info = []
        disk_partitions = psutil.disk_partitions()
        disk_count = 1
        for partition in disk_partitions:
            if 'rw' in partition.opts:  # Filter out non-disk partitions (like CD-ROM)
                disk_usage = psutil.disk_usage(partition.mountpoint)
                free_space_gb = disk_usage.free / (1024 ** 3)  # Convert bytes to gigabytes
                total_space_gb = disk_usage.total / (1024 ** 3)
                disk_label = f"disk_{disk_count}"
                disk_info.append({
                    'label': disk_label,
                    'mountpoint': partition.mountpoint,
                    'free_space': round(free_space_gb, 2),
                    'total_space': round(total_space_gb, 2)
                })
                disk_count += 1
        system_info['Disks'] = disk_info
        


        result['success'] = True
        result['data'] = system_info
    except Exception as e:
        result['error'] = str(e)
    
    return jsonify(result)