"""CLI interface using typer."""
import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler

from .config import Config

# Create typer app
app = typer.Typer(
    name="devops-tool",
    help="DevOps automation tool with config and logging",
    add_completion=False,
)

console = Console()


def setup_logging(config: Config) -> None:
    """Setup logging based on config.
    
    Args:
        config: Configuration object
    """
    log_level = config.get("logging.level", "INFO")
    log_format = config.get("logging.format")
    log_file = config.get("logging.file")
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging with rich handler for console
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            RichHandler(console=console, rich_tracebacks=True),
            logging.FileHandler(log_file) if log_file else logging.NullHandler(),
        ],
    )


@app.command()
def run(
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file (default: config.yaml)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output (DEBUG level)",
    ),
) -> None:
    """Run the devops tool with the given configuration."""
    logger = logging.getLogger(__name__)
    
    try:
        # Load config
        config = Config(config_file)
        
        # Override log level if verbose flag is set
        if verbose:
            config.data["logging"]["level"] = "DEBUG"
        
        # Setup logging
        setup_logging(config)
        
        # Log some info
        logger.info(f"Starting {config.get('app.name')} v{config.get('app.version')}")
        logger.debug(f"Config loaded from: {config.config_path}")
        logger.debug(f"Working directory: {config.get_path('paths.workdir')}")
        
        # Your actual tool logic goes here
        console.print("[green]✓[/green] DevOps tool is running!")
        console.print(f"Config: {config.config_path}")
        console.print(f"Log level: {config.get('logging.level')}")
        
        # Example of using pathlib
        output_dir = config.get_path("paths.output")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory created: {output_dir.absolute()}")
        
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        logger.exception("Unexpected error occurred")
        raise typer.Exit(code=1)


@app.command()
def info() -> None:
    """Show information about the tool and configuration."""
    try:
        config = Config()
        console.print(f"[bold]App:[/bold] {config.get('app.name')}")
        console.print(f"[bold]Version:[/bold] {config.get('app.version')}")
        console.print(f"[bold]Config file:[/bold] {config.config_path}")
        console.print(f"[bold]Log level:[/bold] {config.get('logging.level')}")
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1)


def main() -> None:
    """Entry point for the CLI."""
    app()
