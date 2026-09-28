import os
import json
import shutil

CONFIG_FILE = "config.json"

class ModManagerBackend:
    def __init__(self):
        self.game_dir = ""
        self.mods = []
        self.mods_dir = "installed_mods"
        if not os.path.exists(self.mods_dir):
            os.makedirs(self.mods_dir)
        self.load_config()
        self.load_managed_mods()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    self.game_dir = config.get("game_dir", "")
                    self.active_mods = config.get("active_mods", {})
            except Exception as e:
                self.active_mods = {}
                print(f"Error loading config: {e}")
        else:
            self.active_mods = {}

    def load_managed_mods(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.mods = config.get("managed_mods", [])
        except:
            self.mods = []

    def save_config(self):
        try:
            config = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
            config["game_dir"] = self.game_dir
            config["active_mods"] = self.active_mods
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def save_managed_mods(self):
        try:
            config = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
            config["managed_mods"] = self.mods
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving managed mods: {e}")

    def set_game_dir(self, directory):
        self.game_dir = directory
        self.save_config()

    def get_mod_status(self, mod_filename):
        data_dir = os.path.join(self.game_dir, "data")
        active_path = os.path.join(data_dir, mod_filename)
        disabled_path = os.path.join(data_dir, mod_filename + ".disabled")
        
        is_active = os.path.exists(active_path)
        is_disabled = os.path.exists(disabled_path)
        
        if is_active:
            return "Active"
        elif is_disabled:
            return "Disabled"
        return "Missing"

    def add_mod(self, file_path, overwrite=False):
        data_dir = os.path.join(self.game_dir, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            
        filename = os.path.basename(file_path)
        dest_path = os.path.join(data_dir, filename)
        
        if os.path.exists(dest_path) or os.path.exists(dest_path + ".disabled"):
            if not overwrite:
                return False, f"{filename} already exists"
                
        shutil.copy2(file_path, dest_path)
        if filename not in self.mods:
            self.mods.append(filename)
            self.save_managed_mods()
        return True, ""

    def toggle_mod(self, mod_filename, currently_active):
        data_dir = os.path.join(self.game_dir, "data")
        active_path = os.path.join(data_dir, mod_filename)
        disabled_path = os.path.join(data_dir, mod_filename + ".disabled")
        
        if currently_active:
            if os.path.exists(active_path):
                os.rename(active_path, disabled_path)
        else:
            if os.path.exists(disabled_path):
                os.rename(disabled_path, active_path)

    def delete_mod(self, mod_filename):
        data_dir = os.path.join(self.game_dir, "data")
        active_path = os.path.join(data_dir, mod_filename)
        disabled_path = os.path.join(data_dir, mod_filename + ".disabled")
        
        if os.path.exists(active_path):
            os.remove(active_path)
        if os.path.exists(disabled_path):
            os.remove(disabled_path)
            
        if mod_filename in self.mods:
            self.mods.remove(mod_filename)
            self.save_managed_mods()

    def load_scraped_mods(self, mods_dir=None):
        mods_dir = mods_dir or self.mods_dir
        scraped_mods = []
        if not os.path.exists(mods_dir):
            self.scraped_mods = []
            return
            
        for item in os.listdir(mods_dir):
            mod_path = os.path.join(mods_dir, item)
            if os.path.isdir(mod_path):
                manifest_path = os.path.join(mod_path, "manifest.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                            
                        # Extract data
                        name = manifest.get("Name", item)
                        description = manifest.get("Description", "No description available.")
                        thumbnail = manifest.get("IconPath", "")
                        
                        options = manifest.get("Options", [])
                        parsed_options = []
                        if options:
                            for opt in options:
                                parsed_options.append({
                                    "name": opt.get("Name", "Unnamed Option"),
                                    "description": opt.get("Description", "")
                                })
                            if not thumbnail and len(options) > 0:
                                thumbnail = options[0].get("Image", "")
                                
                        thumbnail_path = os.path.join(mod_path, thumbnail) if thumbnail else None
                        if thumbnail_path and not os.path.exists(thumbnail_path):
                            thumbnail_path = None
                            
                        scraped_mods.append({
                            "id": item,
                            "path": mod_path,
                            "name": name,
                            "description": description,
                            "thumbnail_path": thumbnail_path,
                            "options": parsed_options
                        })
                    except Exception as e:
                        print(f"Error parsing {manifest_path}: {e}")
                        
        # Sort based on saved load order
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                load_order = config.get("load_order", [])
                
            mod_dict = {m["id"]: m for m in scraped_mods}
            ordered_mods = []
            for mod_id in load_order:
                if mod_id in mod_dict:
                    ordered_mods.append(mod_dict[mod_id])
                    del mod_dict[mod_id]
            ordered_mods.extend(mod_dict.values())
            self.scraped_mods = ordered_mods
        except:
            self.scraped_mods = scraped_mods

    def save_load_order(self):
        try:
            config = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
            config["load_order"] = [m["id"] for m in self.scraped_mods]
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving load order: {e}")

    def reorder_mod(self, start_idx, target_idx):
        if 0 <= start_idx < len(self.scraped_mods) and 0 <= target_idx < len(self.scraped_mods):
            mod = self.scraped_mods.pop(start_idx)
            self.scraped_mods.insert(target_idx, mod)
            self.save_load_order()

    def install_mod_from_zip(self, zip_path):
        import zipfile
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                mod_name = os.path.splitext(os.path.basename(zip_path))[0]
                extract_path = os.path.join(self.mods_dir, mod_name)
                
                zip_ref.extractall(extract_path)
                
                # Check for single nested folder containing manifest.json
                contents = os.listdir(extract_path)
                if len(contents) == 1 and os.path.isdir(os.path.join(extract_path, contents[0])):
                    subfolder = os.path.join(extract_path, contents[0])
                    if os.path.exists(os.path.join(subfolder, "manifest.json")):
                        for item in os.listdir(subfolder):
                            shutil.move(os.path.join(subfolder, item), os.path.join(extract_path, item))
                        os.rmdir(subfolder)
            
            self.load_scraped_mods()
            return True, f"Successfully installed {mod_name}"
        except Exception as e:
            return False, f"Failed to install zip: {e}"

    def toggle_mod_option(self, mod_id, option_name, is_active):
        if mod_id not in self.active_mods:
            self.active_mods[mod_id] = []
        if is_active:
            if option_name not in self.active_mods[mod_id]:
                self.active_mods[mod_id].append(option_name)
        else:
            if option_name in self.active_mods[mod_id]:
                self.active_mods[mod_id].remove(option_name)
        self.save_config()

    def get_active_files(self):
        files = {}
        conflicts = []
        for mod in self.scraped_mods:
            mod_id = mod["id"]
            if mod_id not in self.active_mods or not self.active_mods[mod_id]:
                continue
            
            active_opts = self.active_mods[mod_id]
            
            manifest_path = os.path.join(mod["path"], "manifest.json")
            if not os.path.exists(manifest_path):
                continue
                
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                    
                for opt in manifest.get("Options", []):
                    opt_name = opt.get("Name")
                    if opt_name in active_opts:
                        includes = opt.get("Include", [])
                        for inc in includes:
                            inc_path = os.path.join(mod["path"], inc)
                            if os.path.exists(inc_path) and os.path.isdir(inc_path):
                                for root, _, filenames in os.walk(inc_path):
                                    for filename in filenames:
                                        rel_path = os.path.relpath(os.path.join(root, filename), inc_path)
                                        src = os.path.join(root, filename)
                                        
                                        if rel_path in files:
                                            conflicts.append((rel_path, files[rel_path][1], mod_id))
                                        files[rel_path] = (src, mod_id)
            except:
                pass
        return files, conflicts

    def deploy_mods(self):
        self.staging_dir = "staging"
        if os.path.exists(self.staging_dir):
            shutil.rmtree(self.staging_dir)
        os.makedirs(self.staging_dir)
        
        files, conflicts = self.get_active_files()
        
        for dest, (src, _) in files.items():
            staging_dest = os.path.join(self.staging_dir, dest)
            os.makedirs(os.path.dirname(staging_dest), exist_ok=True)
            shutil.copy2(src, staging_dest)
            
        if self.game_dir:
            data_dir = os.path.join(self.game_dir, "data")
            if os.path.exists(data_dir):
                for root, _, filenames in os.walk(self.staging_dir):
                    for filename in filenames:
                        src = os.path.join(root, filename)
                        rel_path = os.path.relpath(src, self.staging_dir)
                        game_dest = os.path.join(data_dir, rel_path)
                        os.makedirs(os.path.dirname(game_dest), exist_ok=True)
                        shutil.copy2(src, game_dest)
        
        return conflicts
