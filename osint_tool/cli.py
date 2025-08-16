import click
import pyfiglet
from rich.console import Console
from osint_tool import exif_module, stego_module, vision_module

console = Console()

# Banner
banner = pyfiglet.figlet_format("OSINT IMAGE ANALYZER")
console.print(f"[cyan]{banner}[/cyan]")
console.print("[white]Developed by [bold]Manoj Kumar | cybergodfather[/bold][/white]")
console.print("[yellow]A CLI-based digital forensics and OSINT tool.[/yellow]")

@click.group()
def cli():
    """OSINT Image Analyzer - Digital Forensics CLI Tool"""
    pass


# ----------------- Stego -----------------
@cli.command()
@click.argument("image_path")
@click.option("--password", "-p", help="Password for steghide extraction")
@click.option("--wordlist", "-w", help="Password wordlist for brute force")
def stego(image_path, password, wordlist):
    """Check for hidden data (steganography) in image"""
    stego_module.check_stego(image_path, password=password, wordlist=wordlist)


# ----------------- Exif -----------------
@cli.command()
@click.argument("image_path")
def exif(image_path):
    """Extract EXIF metadata from image"""
    data = exif_module.extract_exif(image_path)
    if data:
        console.print("[bold green]EXIF Data Found:[/bold green]")
        for tag, value in data.items():
            console.print(f"[cyan]{tag}[/cyan]: {value}")
    else:
        console.print("[bold red]No EXIF metadata found![/bold red]")


# ----------------- Vision -----------------
@cli.command()
@click.argument("image_path")
def vision(image_path):
    """Run computer vision & forensic analysis on an image"""
    hashes = vision_module.compute_hashes(image_path)
    text = vision_module.extract_text(image_path)
    ela_output = vision_module.error_level_analysis(image_path)

    console.print("\n[bold cyan]=== Image Hashes ===[/bold cyan]")
    for k, v in hashes.items():
        console.print(f"{k}: {v}")

    console.print("\n[bold cyan]=== Extracted Text (OCR) ===[/bold cyan]")
    console.print(text if text else "No text detected")

    console.print(f"\n[bold cyan]=== ELA Output ===[/bold cyan]\nSaved to: {ela_output}")


# ----------------- Full Analysis -----------------
@cli.command()
@click.argument("image_path")
def analyze(image_path):
    """Run full analysis (EXIF + Stego + Vision)"""
    console.print("[bold yellow]Running full analysis...[/bold yellow]")
    exif(image_path)
    stego(image_path)
    vision(image_path)


if __name__ == "__main__":
    cli()
