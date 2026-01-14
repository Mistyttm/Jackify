#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Engine Service Module
Handles downloading and managing the jackify-engine binary from GitHub releases
"""

import os
import sys
import logging
import requests
import tarfile
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import shutil

logger = logging.getLogger(__name__)


class EngineService:
    """Service for managing jackify-engine installation and updates"""
    
    GITHUB_REPO = "Omni-guides/dev-jackify-engine"
    ENGINE_BINARY_NAME = "jackify-engine"
    
    def __init__(self):
        self.logger = logger
    
    def get_engine_install_dir(self) -> Path:
        """
        Get the directory where jackify-engine should be installed.
        
        Returns:
            Path to engine installation directory
        """
        from shared.paths import get_jackify_data_dir
        
        # For AppImage: engine is bundled at APPDIR/opt/jackify/engine/
        appdir = os.environ.get('APPDIR')
        if appdir and sys.argv[0] and 'jackify' in sys.argv[0].lower() and '/tmp/.mount_' in sys.argv[0]:
            # Running from Jackify AppImage - use bundled engine location
            return Path(appdir) / 'opt' / 'jackify' / 'engine'
        
        # For source/development: use user data directory
        engine_dir = get_jackify_data_dir() / "engine"
        engine_dir.mkdir(parents=True, exist_ok=True)
        return engine_dir
    
    def get_engine_path(self) -> Optional[Path]:
        """
        Get the path to the jackify-engine binary.
        
        Returns:
            Path to jackify-engine binary if found, None otherwise
        """
        engine_dir = self.get_engine_install_dir()
        engine_path = engine_dir / self.ENGINE_BINARY_NAME
        
        if engine_path.exists() and os.access(engine_path, os.X_OK):
            return engine_path
        
        return None
    
    def is_engine_installed(self) -> bool:
        """Check if jackify-engine is installed"""
        return self.get_engine_path() is not None
    
    def get_latest_release_info(self) -> Optional[dict]:
        """
        Fetch latest release information from GitHub.
        
        Returns:
            Dictionary with release info or None on failure
        """
        try:
            url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            
            # Find the Linux x64 asset
            asset = None
            for a in release_data.get('assets', []):
                if 'linux-x64' in a['name'].lower() and a['name'].endswith('.tar.gz'):
                    asset = a
                    break
            
            if not asset:
                self.logger.error("No linux-x64 release asset found")
                return None
            
            return {
                'version': release_data['tag_name'],
                'download_url': asset['browser_download_url'],
                'size': asset['size'],
                'name': asset['name']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fetch latest release info: {e}")
            return None
    
    def download_and_install_engine(self, progress_callback=None) -> Tuple[bool, Optional[str]]:
        """
        Download and install the latest jackify-engine release.
        
        Args:
            progress_callback: Optional callback(current, total) for progress updates
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Get latest release info
            release_info = self.get_latest_release_info()
            if not release_info:
                return False, "Failed to fetch latest release information"
            
            self.logger.info(f"Downloading jackify-engine {release_info['version']}...")
            
            # Download to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as tmp_file:
                tmp_path = tmp_file.name
                
                response = requests.get(release_info['download_url'], stream=True, timeout=30)
                response.raise_for_status()
                
                total_size = release_info['size']
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            # Extract to installation directory
            engine_dir = self.get_engine_install_dir()
            
            # Remove old engine if exists
            old_engine = engine_dir / self.ENGINE_BINARY_NAME
            if old_engine.exists():
                old_engine.unlink()
            
            # Extract tarball
            self.logger.info(f"Extracting to {engine_dir}...")
            with tarfile.open(tmp_path, 'r:gz') as tar:
                tar.extractall(engine_dir)
            
            # Ensure engine is executable
            engine_path = engine_dir / self.ENGINE_BINARY_NAME
            if engine_path.exists():
                engine_path.chmod(0o755)
                self.logger.info(f"Successfully installed jackify-engine {release_info['version']}")
            else:
                return False, f"Engine binary not found after extraction: {engine_path}"
            
            # Clean up
            os.unlink(tmp_path)
            
            return True, None
            
        except Exception as e:
            error_msg = f"Failed to download/install engine: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def ensure_engine_installed(self, auto_download: bool = True) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Ensure jackify-engine is installed, optionally downloading if missing.
        
        Args:
            auto_download: If True, automatically download if not found
            
        Returns:
            Tuple of (success, engine_path, error_message)
        """
        # Check if already installed
        engine_path = self.get_engine_path()
        if engine_path:
            self.logger.debug(f"Found jackify-engine at: {engine_path}")
            return True, engine_path, None
        
        # Not installed - download if allowed
        if not auto_download:
            return False, None, "jackify-engine not installed"
        
        self.logger.info("jackify-engine not found, downloading latest release...")
        success, error = self.download_and_install_engine()
        
        if not success:
            return False, None, error
        
        # Verify installation
        engine_path = self.get_engine_path()
        if not engine_path:
            return False, None, "Engine installation succeeded but binary not found"
        
        return True, engine_path, None
