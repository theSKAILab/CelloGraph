
from grobid_client.grobid_client import GrobidClient


client = GrobidClient(config_path="./grobid_client_python/config.json")
client.process("processFulltextDocument", "./scitex/pdfs", output="./scitex/outputs/")