import asyncio
import docker
from flask import jsonify, Blueprint
from docker.errors import DockerException

docker_bp = Blueprint('docker', __name__)

async def fetch_container_info(container):
    container_info = {
        'id': container.id,
        'name': container.name,
        'status': container.status,
        'image': container.image.tags[0] if container.image.tags else 'N/A',
        'created': container.attrs['Created'],
        'ports': container.attrs['HostConfig']['PortBindings'] if 'HostConfig' in container.attrs else 'N/A',
        'volumes': container.attrs['HostConfig']['Binds'] if 'HostConfig' in container.attrs else [],
        'labels': container.labels
    }
    
    if container.status == 'running':
        try:
            stats = await asyncio.to_thread(container.stats, stream=False)
            print('stats: ', stats)
            memory_usage_gb = stats['memory_stats']['usage'] / (1024 ** 3)
            memory_limit_gb = stats['memory_stats']['limit'] / (1024 ** 3)
            container_info['memory_stats'] = {
                'usage_gb': round(memory_usage_gb, 2),
                'limit_gb': round(memory_limit_gb, 2)
            }
            
            # Calculate disk space usage
            if 'blkio_stats' in stats and 'io_service_bytes_recursive' in stats['blkio_stats']:
                disk_usage_bytes = sum(entry['value'] for entry in stats['blkio_stats']['io_service_bytes_recursive'] if entry['op'] == 'Write')
                disk_usage_gb = disk_usage_bytes / (1024 ** 3)
                container_info['disk_usage_gb'] = round(disk_usage_gb, 2)
            else:
                container_info['disk_usage_gb'] = 'N/A'
            
            logs = await asyncio.to_thread(container.logs)
            container_info['logs'] = logs.decode('utf-8')
        except Exception as e:
            container_info['memory_stats'] = 'N/A'
            container_info['disk_usage_gb'] = 'N/A'
            container_info['logs'] = str(e)
    else:
        container_info['memory_stats'] = 'N/A'
        container_info['disk_usage_gb'] = 'N/A'
        container_info['logs'] = 'N/A'
    
    return container_info



# Get docker basic data
@docker_bp.route('/docker_info', methods=['GET'])
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
        container_tasks = [fetch_container_info(container) for container in containers]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        container_info_list = loop.run_until_complete(asyncio.gather(*container_tasks))
        result['data']['containers'] = container_info_list
    except DockerException as e:
        result['error'] = str(e)
    except Exception as e:
        result['error'] = str(e)
    
    return jsonify(result)
