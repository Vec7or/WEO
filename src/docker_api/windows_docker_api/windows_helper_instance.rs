use std::{env::home_dir, error::Error, fs::File, path::PathBuf};
use tempfile::TempDir;
use crate::wsl_api::WslApi;

pub(super) struct WindowsHelperInstance {
    name: String,
    image_download_url: String,
    image_name: String,
    wsl_storage_path: String,
    wsl_api: WslApi,
}

impl WindowsHelperInstance {
    fn download_image(&self, file_path: &PathBuf) -> Result<(), Box<dyn Error>> {
        let mut file = File::create(file_path)?;
        let mut res = reqwest::blocking::get(self.image_download_url.clone())?;
        res.copy_to(& mut file)?;
        return Ok(());
    }

    fn instance_exists(&self) -> bool {

        let output = std::process::Command::new("wsl")
            .arg("-l")
            .arg("-q")
            .output()
            .expect("Failed to execute command");
        let mut output_str = String::from_utf8(output.stdout)
            .expect("Failed to convert output to string");
        output_str = output_str.replace("\0", "");
        let mut exists = output_str
            .lines()
            .filter(|line| *line == self.name)
            .peekable();
        if exists.peek().is_some() {
            return true;
        } else {
            return false;
        }
    }

    fn orchestrate_instance(&self) {
        let dir = TempDir::new()
            .expect("Failed to create temporary directory");
        let download_file_path = dir.path().join(self.image_name.clone());
        self.download_image(&download_file_path)
            .expect("Failed to download image");
        println!("Image downloaded to: {:?}", download_file_path);
        let instance_storage_path = PathBuf::from(&self.wsl_storage_path).join(&self.name);
        let output = std::process::Command::new("wsl")
            .arg("--import")
            .arg(&self.name)
            .arg(instance_storage_path.to_str().unwrap())
            .arg(download_file_path)
            .output()
            .expect("Failed to execute command"); 
        if output.status.success() {
            println!("WSL instance created successfully");
        } else {
            panic!("Failed to create WSL instance");
        }
    }

    pub fn new() -> Self {
        let wsl_storage_path = match home_dir() {
            Some(path) => path.join("wsl"),
            None => panic!("Failed to get home directory"),
        };
        let instance = Self {
            name: "weo_orchestrator".to_string(),
            image_download_url: "https://dl-cdn.alpinelinux.org/alpine/v3.20/releases/x86_64/alpine-minirootfs-3.20.3-x86_64.tar.gz".to_string(),
            image_name: "alpine-minirootfs-3.20.3-x86_64.tar.gz".to_string(),
            wsl_storage_path: wsl_storage_path.to_str().unwrap().to_string(),
            wsl_api: WslApi::new(&wsl_storage_path.to_str().unwrap().to_string()),
        };
        if !instance.instance_exists()  
        {
            println!("Instance does not exist, creating it");
            instance.orchestrate_instance();

        }
        return instance;
    }
    
    pub fn run_command(&self) -> &str {
        &self.name
    }
}