from flask import Flask, jsonify
import psutil
import docker
from flask_cors import CORS
from docker.errors import DockerException

app = Flask(__name__)
CORS(app)


# Get docker basic data
@app.route('/docker_info', methods=['GET'])
def docker_info():
    result = {'success': False, 'error': None, 'data': None}
    
    try:
        client = docker.from_env()
        client.ping()
        result['success'] = True
        result['data'] = {
            'is_docker_installed': True,
            'is_docker_running': True,
            'containers': []
        }
        
        containers = client.containers.list(all=True)
        for container in containers:
            container_info = {
                'id': container.id,
                'name': container.name,
                'status': container.status,
                'image': container.image.tags[0] if container.image.tags else 'N/A',
                'created': container.attrs['Created'],
                'ports': container.attrs['HostConfig']['PortBindings'] if 'HostConfig' in container.attrs else 'N/A',
                'volumes': container.attrs['HostConfig']['Binds'] if 'HostConfig' in container.attrs else [],
                'memory_stats': container.stats(stream=False)['memory_stats'] if container.status == 'running' else 'N/A',
                'cpu_stats': container.stats(stream=False)['cpu_stats'] if container.status == 'running' else 'N/A',
                'labels': container.labels,
                'logs': container.logs().decode('utf-8') if container.status == 'running' else 'N/A'
            }
            result['data']['containers'].append(container_info)
    except DockerException as e:
        result['error'] = str(e)
    except Exception as e:
        result['error'] = str(e)
    
    return jsonify(result)

# Gets system information RAM - DISK SPACE - NETWORK STATS - CPU CORES
@app.route('/system_info',  methods=['GET'])
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

        total_ram_gb = mem_info.total / (1024 ** 3)  # Convert bytes to gigabytes
        system_info['Total RAM'] = round(total_ram_gb, 2)

        free_ram_gb = mem_info.available / (1024 ** 3)  # Convert bytes to gigabytes
        system_info['Available RAM'] = round(free_ram_gb, 2)

        used_ram_percentage = mem_info.percent
        system_info['RAM Used Percentage'] = round(used_ram_percentage, 2)

        # Disk information
        disk_info = None
        disk_partitions = psutil.disk_partitions()
        print('disk partition', disk_partitions)
        for partition in disk_partitions:
            if 'rw' in partition.opts:  # Filter out non-disk partitions (like CD-ROM)
                disk_usage = psutil.disk_usage(partition.mountpoint)
                free_space_gb = disk_usage.free / (1024 ** 3)  # Convert bytes to gigabytes
                disk_info = round(free_space_gb, 2)
        system_info['Disk Space'] = disk_info

        # Network information
        net_info = psutil.net_io_counters()
        upload_speed = net_info.bytes_sent / 1024 / 1024  # Convert bytes to megabits
        download_speed = net_info.bytes_recv / 1024 / 1024  # Convert bytes to megabits
        system_info['Upload Speed'] = round(upload_speed, 2)
        system_info['Download Speed'] = round(download_speed, 2)

        result['success'] = True
        result['data'] = system_info
    except Exception as e:
        result['error'] = str(e)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
