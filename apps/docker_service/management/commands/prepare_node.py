from django.core.management.base import BaseCommand

from docker_service.models import Node
from docker_service.services.node_processor import NodeProcessor



class Command(BaseCommand):
    help = 'Operation of prapre node'

    def add_arguments(self, parser):
        parser.add_argument('node_id', type=str, help='Node Id')


    def handle(self, *args, **options):
        node_id = options['node_id']
        node = Node.objects.filter(id=node_id).first()
        if not node:
            print(f"Node {node_id} not finded")
            return
        try:
            processor = NodeProcessor(node)
            result, error = processor.prepare_node()
            if error:
                print(f"Node {node_id} preprare error: {error}")
                return
        except Exception as e:
            print(f"Node {node_id} preprare exception: {e}")
            return
        node.is_prepared = result
        node.save()
        print(f"Node {node_id} prepared, status: {result}")
        