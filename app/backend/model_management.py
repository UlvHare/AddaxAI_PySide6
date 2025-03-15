# backend/model_management.py
"""
Handles model loading, storage, and management.
"""
import os
import re
import json
import shutil
import zipfile
import hashlib
import requests
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from . import AddaxAI_files

class ModelManager:
    """Class for managing ML models (downloading, storing, and loading)."""

    def __init__(self, models_dir=None, progress_callback=None):
        """Initialize the model manager.

        Args:
            models_dir: Directory to store models (default: AddaxAI_files/models)
            progress_callback: Function to call with progress updates
        """
        if models_dir is None:
            self.models_dir = os.path.join(AddaxAI_files, "models")
        else:
            self.models_dir = models_dir

        self.progress_callback = progress_callback
        self.catalog_file = os.path.join(self.models_dir, "model_catalog.json")

        # Create models directory if it doesn't exist
        Path(self.models_dir).mkdir(parents=True, exist_ok=True)

        # Initialize or load the model catalog
        self._initialize_catalog()

    def _initialize_catalog(self):
        """Initialize or load the model catalog."""
        if not os.path.exists(self.catalog_file):
            # Create a new catalog file
            self._save_catalog({
                "models": {},
                "default_model": None
            })

    def _load_catalog(self):
        """Load the model catalog from file.

        Returns:
            dict: The model catalog
        """
        if not os.path.exists(self.catalog_file):
            return {"models": {}, "default_model": None}

        try:
            with open(self.catalog_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading model catalog: {str(e)}")
            return {"models": {}, "default_model": None}

    def _save_catalog(self, catalog):
        """Save the model catalog to file.

        Args:
            catalog: Catalog dictionary to save
        """
        try:
            with open(self.catalog_file, 'w') as f:
                json.dump(catalog, f, indent=2)
        except Exception as e:
            print(f"Error saving model catalog: {str(e)}")

    def get_available_models(self):
        """Get a list of available models.

        Returns:
            list: List of model information dictionaries
        """
        catalog = self._load_catalog()
        models = []

        for model_id, model_info in catalog["models"].items():
            model_entry = model_info.copy()
            model_entry["id"] = model_id
            model_entry["is_default"] = (model_id == catalog["default_model"])
            models.append(model_entry)

        return models

    def get_default_model(self):
        """Get the default model information.

        Returns:
            dict: Default model information or None if no default is set
        """
        catalog = self._load_catalog()
        default_id = catalog.get("default_model")

        if default_id and default_id in catalog["models"]:
            model_info = catalog["models"][default_id].copy()
            model_info["id"] = default_id
            model_info["is_default"] = True
            return model_info

        return None

    def set_default_model(self, model_id):
        """Set the default model.

        Args:
            model_id: ID of the model to set as default

        Returns:
            bool: True if successful, False otherwise
        """
        catalog = self._load_catalog()

        if model_id not in catalog["models"]:
            return False

        catalog["default_model"] = model_id
        self._save_catalog(catalog)
        return True

    def download_model(self, model_url, model_name, model_type, description=None, overwrite=False):
        """Download a model from a URL.

        Args:
            model_url: URL to download the model from
            model_name: Name for the downloaded model
            model_type: Type of model (detection, classification, etc.)
            description: Optional description of the model
            overwrite: Whether to overwrite existing model with same name

        Returns:
            dict: Information about the downloaded model, or None if failed
        """
        try:
            # Generate model ID from name
            model_id = self._generate_model_id(model_name)

            # Check if model already exists
            catalog = self._load_catalog()
            if model_id in catalog["models"] and not overwrite:
                print(f"Model with ID {model_id} already exists")
                return None

            # Update progress
            if self.progress_callback:
                self.progress_callback(status="starting", message=f"Downloading model {model_name}...")

            # Create temporary file for download
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_file:
                temp_path = temp_file.name

            # Download the model
            response = requests.get(model_url, stream=True)
            response.raise_for_status()

            # Get file size for progress calculation
            file_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            # Write to temporary file with progress updates
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Update progress
                        if file_size > 0 and self.progress_callback:
                            progress = int((downloaded / file_size) * 100)
                            self.progress_callback(
                                status="downloading",
                                progress=progress,
                                message=f"Downloading {model_name}... {progress}%"
                            )

            # Extract model info and add to catalog
            model_info = self._process_downloaded_model(
                temp_path, model_id, model_name, model_type, description
            )

            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass

            return model_info

        except Exception as e:
            print(f"Error downloading model: {str(e)}")

            # Update progress with error
            if self.progress_callback:
                self.progress_callback(status="error", message=f"Error downloading model: {str(e)}")

            return None

    def import_model(self, model_path, model_name, model_type, description=None, overwrite=False):
        """Import a model from a local file.

        Args:
            model_path: Path to the model file
            model_name: Name for the imported model
            model_type: Type of model (detection, classification, etc.)
            description: Optional description of the model
            overwrite: Whether to overwrite existing model with same name

        Returns:
            dict: Information about the imported model, or None if failed
        """
        try:
            # Generate model ID from name
            model_id = self._generate_model_id(model_name)

            # Check if model already exists
            catalog = self._load_catalog()
            if model_id in catalog["models"] and not overwrite:
                print(f"Model with ID {model_id} already exists")
                return None

            # Update progress
            if self.progress_callback:
                self.progress_callback(status="starting", message=f"Importing model {model_name}...")

            # Extract model info and add to catalog
            model_info = self._process_downloaded_model(
                model_path, model_id, model_name, model_type, description
            )

            return model_info

        except Exception as e:
            print(f"Error importing model: {str(e)}")

            # Update progress with error
            if self.progress_callback:
                self.progress_callback(status="error", message=f"Error importing model: {str(e)}")

            return None

    def _process_downloaded_model(self, model_path, model_id, model_name, model_type, description):
        """Process a downloaded or imported model file.

        Args:
            model_path: Path to the model file
            model_id: ID for the model
            model_name: Name for the model
            model_type: Type of model (detection, classification, etc.)
            description: Optional description of the model

        Returns:
            dict: Information about the processed model, or None if failed
        """
        try:
            # Create model directory
            model_dir = os.path.join(self.models_dir, model_id)
            Path(model_dir).mkdir(parents=True, exist_ok=True)

            # Update progress
            if self.progress_callback:
                self.progress_callback(status="extracting", message=f"Extracting model {model_name}...")

            # Extract if it's a zip file
            if zipfile.is_zipfile(model_path):
                with zipfile.ZipFile(model_path, 'r') as zip_ref:
                    zip_ref.extractall(model_dir)
            else:
                # Copy the model file directly
                shutil.copy2(model_path, os.path.join(model_dir, os.path.basename(model_path)))

            # Calculate hash for model files
            model_hash = self._calculate_directory_hash(model_dir)

            # Find model configuration file
            config_file = self._find_model_config(model_dir)

            # Create model info
            model_info = {
                "name": model_name,
                "type": model_type,
                "description": description or "",
                "hash": model_hash,
                "path": model_dir,
                "config_file": config_file,
                "date_added": self._get_current_timestamp()
            }

            # Add to catalog
            catalog = self._load_catalog()
            catalog["models"][model_id] = model_info

            # Set as default if it's the first model
            if not catalog["default_model"]:
                catalog["default_model"] = model_id

            self._save_catalog(catalog)

            # Update progress
            if self.progress_callback:
                self.progress_callback(status="complete", message=f"Model {model_name} is ready")

            # Return model info with ID
            result = model_info.copy()
            result["id"] = model_id
            result["is_default"] = (model_id == catalog["default_model"])

            return result

        except Exception as e:
            print(f"Error processing model: {str(e)}")

            # Update progress with error
            if self.progress_callback:
                self.progress_callback(status="error", message=f"Error processing model: {str(e)}")

            return None

    def _generate_model_id(self, model_name):
        """Generate a model ID from a model name.

        Args:
            model_name: Name of the model

        Returns:
            str: Model ID
        """
        # Convert to lowercase, replace spaces with underscores
        base_id = re.sub(r'[^a-z0-9_]', '', model_name.lower().replace(' ', '_'))

        # Ensure ID is not empty
        if not base_id:
            base_id = "model"

        return base_id

    def _calculate_directory_hash(self, directory):
        """Calculate a hash for a directory's contents.

        Args:
            directory: Path to the directory

        Returns:
            str: Hash value
        """
        hash_obj = hashlib.md5()

        for root, _, files in os.walk(directory):
            for file in sorted(files):
                file_path = os.path.join(root, file)

                # Skip temporary files
                if file.startswith('.') or file.endswith('.tmp'):
                    continue

                # Update hash with file path and contents
                rel_path = os.path.relpath(file_path, directory)
                hash_obj.update(rel_path.encode())

                with open(file_path, 'rb') as f:
                    # Read in chunks to handle large files
                    for chunk in iter(lambda: f.read(4096), b''):
                        hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def _find_model_config(self, model_dir):
        """Find the configuration file for a model.

        Args:
            model_dir: Path to the model directory

        Returns:
            str: Relative path to the config file, or None if not found
        """
        # Common config file names
        config_names = [
            'model.json', 'config.json', 'model_config.json',
            'model.yaml', 'config.yaml', 'model_config.yaml',
            'model.yml', 'config.yml', 'model_config.yml'
        ]

        # Search for config files
        for root, _, files in os.walk(model_dir):
            for file in files:
                if file in config_names:
                    return os.path.relpath(os.path.join(root, file), model_dir)

        return None

    def _get_current_timestamp(self):
        """Get the current timestamp in ISO format.

        Returns:
            str: Current timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()

    def remove_model(self, model_id):
        """Remove a model.

        Args:
            model_id: ID of the model to remove

        Returns:
            bool: True if successful, False otherwise
        """
        catalog = self._load_catalog()

        if model_id not in catalog["models"]:
            return False

        # Get model directory
        model_dir = catalog["models"][model_id]["path"]

        # Remove model directory
        try:
            if os.path.exists(model_dir):
                shutil.rmtree(model_dir)
        except Exception as e:
            print(f"Error removing model directory: {str(e)}")
            return False

        # Update default model if needed
        if catalog["default_model"] == model_id:
            # Set another model as default if available
            if catalog["models"]:
                catalog["default_model"] = next(iter(catalog["models"]))
            else:
                catalog["default_model"] = None

        # Remove from catalog
        del catalog["models"][model_id]
        self._save_catalog(catalog)

        return True

    def get_model_path(self, model_id=None):
        """Get the path to a model.

        Args:
            model_id: ID of the model (if None, returns default model path)

        Returns:
            str: Path to the model, or None if not found
        """
        catalog = self._load_catalog()

        if model_id is None:
            model_id = catalog.get("default_model")

            if not model_id:
                return None

        if model_id not in catalog["models"]:
            return None

        return catalog["models"][model_id]["path"]

    def get_model_info(self, model_id=None):
        """Get information about a model.

        Args:
            model_id: ID of the model (if None, returns default model info)

        Returns:
            dict: Model information, or None if not found
        """
        catalog = self._load_catalog()

        if model_id is None:
            model_id = catalog.get("default_model")

            if not model_id:
                return None

        if model_id not in catalog["models"]:
            return None

        model_info = catalog["models"][model_id].copy()
        model_info["id"] = model_id
        model_info["is_default"] = (model_id == catalog["default_model"])

        return model_info

def get_available_models(models_dir=None):
    """Get a list of available models.

    Args:
        models_dir: Custom models directory (optional)

    Returns:
        list: List of model information dictionaries
    """
    manager = ModelManager(models_dir)
    return manager.get_available_models()


def get_default_model(models_dir=None):
    """Get the default model information.

    Args:
        models_dir: Custom models directory (optional)

    Returns:
        dict: Default model information or None if no default is set
    """
    manager = ModelManager(models_dir)
    return manager.get_default_model()


def get_model_path(model_id=None, models_dir=None):
    """Get the path to a model.

    Args:
        model_id: ID of the model (if None, returns default model path)
        models_dir: Custom models directory (optional)

    Returns:
        str: Path to the model, or None if not found
    """
    manager = ModelManager(models_dir)
    return manager.get_model_path(model_id)


def download_model(model_url, model_name, model_type, description=None,
                  overwrite=False, models_dir=None, progress_callback=None):
    """Download a model from a URL.

    Args:
        model_url: URL to download the model from
        model_name: Name for the downloaded model
        model_type: Type of model (detection, classification, etc.)
        description: Optional description of the model
        overwrite: Whether to overwrite existing model with same name
        models_dir: Custom models directory (optional)
        progress_callback: Function to call with progress updates

    Returns:
        dict: Information about the downloaded model, or None if failed
    """
    manager = ModelManager(models_dir, progress_callback)
    return manager.download_model(model_url, model_name, model_type, description, overwrite)
