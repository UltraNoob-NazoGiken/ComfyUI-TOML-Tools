import os
import toml
import folder_paths
import random
# test
# --- ここを追加 ---
# ComfyUIの型チェックを騙して、どんな型でも接続できるようにする魔法のクラス
class AnyType(str):
    def __ne__(self, __value):
        return False
    def __eq__(self, __value):
        return True
# ------------------

# データの受け渡し用に定義する型
TOML_DATA_TYPE = "TOML_DATA"

class LoadTomlNode:
    """
    1. TOMLファイルを読み込むノード
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": "config.toml", "multiline": False}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = (TOML_DATA_TYPE,)
    RETURN_NAMES = ("toml_data",)
    FUNCTION = "load_toml"
    CATEGORY = "TOML Tools"
    

    @classmethod
    def load_toml(self, file_path, seed=0):
        random.seed(seed)
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return ({},)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = toml.load(f)
            return (data,)
        except Exception as e:
            print(f"Error loading TOML: {e}")
            return ({},)

class GetTomlValueNode:
    """
    2. 値を取り出すノード
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "toml_data": (TOML_DATA_TYPE,),
                "key": ("STRING", {"default": "section.variable_name"}),
            },
            "optional": {
                "default_value": ("STRING", {"default": "0"}), 
            }
        }

    RETURN_TYPES = ("STRING", "INT", "FLOAT", AnyType("*")) # 出力もAnyTypeにしておくと安心
    RETURN_NAMES = ("string_val", "int_val", "float_val", "raw_val")
    FUNCTION = "get_value"
    CATEGORY = "TOML Tools"

    def get_value(self, toml_data, key, default_value="0"):
        keys = key.split(".")
        value = toml_data
        found = True
        try:
            for k in keys:
                value = value[k]
        except (KeyError, TypeError):
            found = False
            print(f"Key '{key}' not found. Using default: {default_value}")

        if not found:
            value = default_value

        str_v = str(value)
        try:
            int_v = int(float(value))
        except (ValueError, TypeError):
            int_v = 0
        try:
            float_v = float(value)
        except (ValueError, TypeError):
            float_v = 0.0
        
        return (str_v, int_v, float_v, value)


class CreateTomlDataNode:
    """
    3. Key/ValueのペアからTOMLデータ(辞書)を作成するノード
    ★ここを修正しました★
    """
    @classmethod
    def INPUT_TYPES(cls):
        inputs = {"required": {}, "optional": {}}
        for i in range(1, 6):
            inputs["optional"][f"key_{i}"] = ("STRING", {"default": ""})
            # ここで "*" の代わりに AnyType("*") を使うことでエラーを回避
            inputs["optional"][f"value_{i}"] = (AnyType("*"), {}) 
        return inputs

    RETURN_TYPES = (TOML_DATA_TYPE,)
    RETURN_NAMES = ("toml_data",)
    FUNCTION = "create_data"
    CATEGORY = "TOML Tools"

    def create_data(self, **kwargs):
        new_data = {}
        
        for i in range(1, 6):
            k_key = f"key_{i}"
            v_key = f"value_{i}"
            
            if k_key in kwargs and v_key in kwargs:
                key_name = kwargs[k_key]
                val = kwargs[v_key]
                
                if not key_name:
                    continue

                if "." in key_name:
                    parts = key_name.split(".")
                    current = new_data
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                        if not isinstance(current, dict):
                             continue 
                    current[parts[-1]] = val
                else:
                    new_data[key_name] = val
        
        return (new_data,)


class MergeTomlDataNode:
    """
    4. 2つのTOMLデータをマージするノード
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "toml_data_A": (TOML_DATA_TYPE,),
                "toml_data_B": (TOML_DATA_TYPE,),
            }
        }

    RETURN_TYPES = (TOML_DATA_TYPE,)
    RETURN_NAMES = ("merged_data",)
    FUNCTION = "merge_data"
    CATEGORY = "TOML Tools"

    def merge_data(self, toml_data_A=None, toml_data_B=None):
        dict_a = toml_data_A if toml_data_A else {}
        dict_b = toml_data_B if toml_data_B else {}
        merged = self.deep_merge(dict_a, dict_b)
        return (merged,)

    def deep_merge(self, dict1, dict2):
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = value
        return result


class SaveTomlNode:
    """
    5. TOMLデータをファイルに保存するノード
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "toml_data": (TOML_DATA_TYPE,),
                "filename(Full_Path)": ("STRING", {"default": "output.toml"}),
                "overwrite": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_path",)
    OUTPUT_NODE = True
    FUNCTION = "save_toml"
    CATEGORY = "TOML Tools"

    def save_toml(self, toml_data, filename, overwrite):
        output_dir = folder_paths.get_output_directory()
        full_path = os.path.join(output_dir, filename)

        if os.path.exists(full_path) and not overwrite:
            print(f"File exists and overwrite is False: {full_path}")
            return (full_path,)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                toml.dump(toml_data, f)
            print(f"Saved TOML to: {full_path}")
        except Exception as e:
            print(f"Error saving TOML: {e}")

        return (full_path,)