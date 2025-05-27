mod docker_api;
use docker_api::DockerApi;
mod wsl_api;
use wsl_api::WslApi;

use std::io::{IsTerminal};

use clap::{Parser, Subcommand};
use colored::Colorize;


#[derive(clap::ValueEnum, Clone, Default, Debug)]
enum LocalDockerType {
    #[default]
    File,
    Dir,
}

#[derive(Parser)]
#[command(about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    /// Creates a new wsl environment
    Create {
        /// The name of the docker image to use as environment base
        #[arg(short, long)]
        docker_image: String,

        /// The name of the new environment that will be created
        #[arg(short, long)]
        environment_name: String,

        /// If this is set the option "-d" will be interpreted as a local path to a dockerfile or to a directory containing a dockerfile and it's build assets dependent on the value.
        #[arg(short, long)]
        local: Option<LocalDockerType>,

        /// The password of the user within the new environment
        #[arg(short, long)]
        password: String,

        /// The user that should be used within the environment. This user needs to exist in the image.
        #[arg(short, long, default_value_t = String::from("root"))]
        user: String,

        /// Whether to print verbose output
        #[arg(short, long, default_value_t = false)]
        verbose: bool,
    },
    /// Removes an existing wsl environment
    Remove {
        /// The name of the environment that will be removed
        #[arg(short, long)]
        environment_name: String,

        /// Whether to print verbose output
        #[arg(short, long, default_value_t = false)]
        verbose: bool,
    },
}

#[rustfmt::skip]
fn print_intro() {
    println!("");
    println!("{}","██     ██     ███████              ██████             ".green());
    println!("{}","██     ██     ██                  ██    ██            ".green());
    println!("{}","██  █  ██     █████               ██    ██            ".green());
    println!("{}","██ ███ ██     ██                  ██    ██            ".green());
    println!("{}"," ███ ███  SL  ███████ NVIRONMENT   ██████  RCHESTRATOR".green());
    println!("{}","                                                      ".green());
}

fn print_version() {
    println!(
        "{} {}",
        "VERSION: ".green(),
        env!("CARGO_PKG_VERSION").green()
    );
}

fn main() {
    // Fancy intro only shown in interactive terminal
    if std::io::stdin().is_terminal() {
        print_intro();
        print_version();
    }

    let _docker_api = DockerApi::new();

    let cli = Cli::parse();
    match &cli.command {
        Some(Commands::Create {
            docker_image,
            environment_name,
            local,
            password,
            user,
            verbose,
        }) => {
            println!("Creating environment: {}", environment_name);
            println!("Using docker image: {}", docker_image);
            println!("Local type: {:?}", local);
            println!("Password: {}", password);
            println!("User: {}", user);
            if *verbose {
                println!("Verbose mode is enabled");
            }
        }
        Some(Commands::Remove {
            environment_name,
            verbose,
        }) => {
            println!("Removing environment: {}", environment_name);
            if *verbose {
                println!("Verbose mode is enabled");
            }
        }
        None => {
            println!("No command provided");
        }
    }
}
