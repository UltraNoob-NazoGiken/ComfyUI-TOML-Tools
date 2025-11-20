from .toml_nodes import LoadTomlNode, GetTomlValueNode, CreateTomlDataNode, MergeTomlDataNode, SaveTomlNode

NODE_CLASS_MAPPINGS = {
    "LoadToml": LoadTomlNode,
    "GetTomlValue": GetTomlValueNode,
    "CreateTomlData": CreateTomlDataNode,
    "MergeTomlData": MergeTomlDataNode,
    "SaveToml": SaveTomlNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadToml": "Load TOML File",
    "GetTomlValue": "Get Value from TOML",
    "CreateTomlData": "Create TOML Data (5 Keys)",
    "MergeTomlData": "Merge TOML Data",
    "SaveToml": "Save TOML File"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]