from datetime import datetime

def create_conversation_item(workspace_id, block_id, conversation_id, model, messages, metadata, status='active'):
    compound_id = f"{workspace_id}#{block_id}#{conversation_id}"
    created_at = datetime.utcnow().isoformat() + 'Z'
    updated_at = created_at

    return {
        'workspace_id': workspace_id,
        'sort_key': compound_id,
        'block_id': block_id,
        'conversation_id': conversation_id,
        'model': model,
        'created_at': created_at,
        'updated_at': updated_at,
        'messages': messages,
        'metadata': metadata,
        'status': status
    } 