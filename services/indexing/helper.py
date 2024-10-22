import os
import uuid
import json

class FileUUIDGenerator:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def generate_unique_uuid(self):
        existing_uuids = self.get_existing_uuids()
        
        # 生成一个新的 UUID
        new_uuid = str(uuid.uuid4())
        
        # 确保新生成的 UUID 不在已有文件名的列表中
        while new_uuid in existing_uuids:
            new_uuid = str(uuid.uuid4())  # 再次生成一个新的 UUID，直到没有冲突
        
        return new_uuid

    def get_existing_uuids(self):
        existing_uuids = set()
        
        # 遍历文件夹下所有文件
        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                # 检查文件名是否是有效的 UUID
                try:
                    uuid_obj = uuid.UUID(file_name)  # 尝试解析文件名为 UUID
                    existing_uuids.add(str(uuid_obj))  # 如果成功，添加到已存在的 UUID 集合中
                except ValueError:
                    # 文件名不是有效的 UUID，忽略
                    pass
        
        return existing_uuids

class LocalFileByteStore:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def mset(self, data):
        for doc_id, doc_content in data:
            file_path = os.path.join(self.folder_path, f"{doc_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(doc_content, f)
    
    def get(self, doc_id):
        file_path = os.path.join(self.folder_path, f"{doc_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Document with id {doc_id} not found.")
            return None
