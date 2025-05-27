#[cfg(target_os = "windows")]
pub struct WslApi {
    storage_path: String,
}

#[cfg(target_os = "windows")]
impl WslApi {
    fn check_version() -> Result<(), String> {
        let output = std::process::Command::new("wsl")
            .arg("--version")
            .output()
            .expect("Failed to execute command");
        if output.status.success() {
            Ok(())
        } else {
            Err("WSL is not installed".to_string())
        }
    }

    pub fn new(storage_path: &str) -> Self {
        Self::check_version()
            .expect("WSL is not installed");
        return Self {
            storage_path: storage_path.to_string(),
        };
    }

    pub fn instance_exists(&self, instance_name: &str) -> bool {
        let output_str = Self::list_instances();
        let mut exists = output_str
            .lines()
            .filter(|line| *line == instance_name)
            .peekable();
        if exists.peek().is_some() {
            return true;
        } else {
            return false;
        }
    }


    pub fn list_instances() -> String {
         let output = std::process::Command::new("wsl")
            .arg("-l")
            .arg("-q")
            .output()
            .expect("Failed to execute command");
        let mut output_str = String::from_utf8(output.stdout)
            .expect("Failed to convert output to string");
        output_str = output_str.replace("\0", "");

        return output_str;
    }

    pub fn import_instance(&self, instance_name: &str, image_path: &str) -> Result<(), String> {
        let output = std::process::Command::new("wsl")
            .arg("--import")
            .arg(instance_name)
            .arg(self.storage_path.to_string())
            .arg(image_path)
            .output()
            .expect("Failed to execute command");
        if output.status.success() {
            Ok(())
        } else {
            Err("Failed to import WSL instance".to_string())
        }
    }

    pub fn remove_instance(&self, instance_name: &str) -> Result<(), String> {
        let output = std::process::Command::new("wsl")
            .arg("--unregister")
            .arg(instance_name)
            .output()
            .expect("Failed to execute command");
        if output.status.success() {
            Ok(())
        } else {
            Err("Failed to remove WSL instance".to_string())
        }
    }

    pub fn run_command_in_instance(&self, instance_name: &str, command: &str, user: Option<&str>) -> Result<String, String> {
        let mut instance_user = "root".to_string();
        if user.is_some() {
            instance_user = user.unwrap().to_string();
        }
        let output = std::process::Command::new("wsl")
            .arg("-u")
            .arg(instance_user)
            .arg("-d")
            .arg(instance_name)
            .arg("sh")
            .arg("-c")
            .arg(command)
            .output()
            .expect("Failed to execute command");
        if output.status.success() {
            let output_str = String::from_utf8(output.stdout)
                .expect("Failed to convert output to string");
            Ok(output_str)
        } else {
            Err("Failed to run command in WSL instance".to_string())
        }
    }

    pub fn file_exists_in_instance(&self, instance_name: &str, file_path: &str) -> Result<bool, String> {
        let output = self.run_command_in_instance(instance_name, format!("test -f {} && echo \"EXISTS\" || echo \"NOT EXISTENT\"", file_path).as_str(), None)
            .expect("Failed to execute command");
        if output.trim() == "EXISTS" {
            Ok(true)
        } else {
            Ok(false)
        }
    }
}