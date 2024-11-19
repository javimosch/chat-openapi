#!/usr/bin/env python3
"""
CLI tool for managing OpenAPI specifications in the chat-openapi system.
"""
import os
import sys
import asyncio
from pathlib import Path
from typing import Optional, List
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.panel import Panel
from rich.syntax import Syntax
from tabulate import tabulate

from app.core.logging import get_logger
from app.services.file_service import FileService
from app.services.vector_storage import VectorStorageService

logger = get_logger(__name__)
console = Console()

# Initialize services
file_service = FileService()
vector_service = VectorStorageService()

def get_uploads_dir() -> Path:
    """Get the uploads directory path."""
    return Path("uploads")

def run_async(coro):
    """Run an async function in the event loop."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def async_command(f):
    """Decorator to run async click commands."""
    def decorator(*args, **kwargs):
        return run_async(f(*args, **kwargs))
    # Preserve the original function's metadata
    decorator.__name__ = f.__name__
    decorator.__doc__ = f.__doc__
    return click.command()(decorator)

@click.group()
def cli():
    """Chat-OpenAPI CLI - Manage your OpenAPI specifications."""
    # Ensure uploads directory exists
    uploads_dir = get_uploads_dir()
    uploads_dir.mkdir(exist_ok=True)

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def upload(file_path: str):
    """Upload a specification file"""
    try:
        # Create UploadFile from path
        file_name = Path(file_path).name
        with open(file_path, 'rb') as f:
            file = UploadFile(filename=file_name, file=f)
            
            # Process the file
            result = asyncio.run(file_service.process_file(file))
            
            # Display results
            console.print(f"Successfully uploaded {file_name}")
            console.print(f"Specification ID: \n{result['spec_id']}")
            
            # Create table
            table = Table(show_header=True)
            table.add_column("Property")
            table.add_column("Value")
            
            table.add_row("Title", result.get('title', 'N/A'))
            table.add_row("Version", result.get('version', 'N/A'))
            table.add_row("Size", f"{result['size'] / 1024:.1f} KB")
            table.add_row("Format", result.get('content_type', 'N/A').upper())
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('spec_id')
def info(spec_id: str):
    """Show detailed information about a specification"""
    try:
        # Get file info
        file_info = file_service.get_file_info(spec_id)
        
        # Get chunk count
        chunk_count = asyncio.run(vector_service.get_chunk_count(spec_id))
        
        console.print(f"[bold]File Information[/bold]")
        console.print(f"ID: {file_info['id']}")
        console.print(f"Name: {file_info['filename']}")
        console.print(f"Size: {file_info['size_formatted']}")
        console.print(f"Format: {file_info['content_type']}")
        console.print(f"Chunks: {chunk_count}")
        console.print(f"Created: {file_info['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        console.print(f"Modified: {file_info['modified_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

@cli.command()
def list():
    """List all specifications"""
    try:
        specs = file_service.list_files()
        
        # Create table
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Size")
        table.add_column("Chunks")
        table.add_column("Modified")
        
        for spec in specs:
            chunk_count = asyncio.run(vector_service.get_chunk_count(spec['id']))
            table.add_row(
                spec['id'],
                spec['filename'],
                spec['size_formatted'],
                str(chunk_count),
                spec['modified_at'].strftime("%Y-%m-%d %H:%M:%S")
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

@cli.command()
@click.argument('spec_id')
@click.argument('output', type=click.Path(), required=False)
def export(spec_id: str, output: Optional[str] = None):
    """Export a specification to a file."""
    uploads_dir = get_uploads_dir()
    found = False
    
    for ext in ['.json', '.yaml', '.yml']:
        source_path = uploads_dir / f"{spec_id}{ext}"
        if source_path.exists():
            found = True
            if output:
                output_path = Path(output)
            else:
                output_path = Path(f"{spec_id}_export{ext}")
            
            with open(source_path, 'rb') as src, open(output_path, 'wb') as dst:
                dst.write(src.read())
            
            console.print(f"[green]Exported to: {output_path}[/green]")
            break
    
    if not found:
        console.print(f"[red]Specification not found: {spec_id}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('spec_id')
def delete(spec_id: str):
    """Remove a specification and its associated chunks"""
    try:
        # Delete file and chunks
        asyncio.run(file_service.delete_file(spec_id))
        
        console.print(f"[green]Successfully deleted specification: {spec_id}[/green]")
        
    except FileNotFoundError:
        console.print(f"[red]Specification not found: {spec_id}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error deleting specification: {str(e)}[/red]")
        sys.exit(1)

@cli.group()
def vector():
    """Vector database management commands."""
    pass

@vector.command(name='size')
@click.option('--detailed', is_flag=True, help='Show detailed size breakdown')
def vector_size(detailed: bool):
    """Show the current size of the vector database."""
    try:
        # Get size information
        size_info = run_async(vector_service.get_collection_size())
        
        if detailed:
            # Create detailed table
            table = Table(title="Vector Database Size")
            table.add_column("Component", style="cyan")
            table.add_column("Size (MB)", justify="right", style="green")
            
            table.add_row("Vectors", f"{size_info['vectors']}")
            table.add_row("Index", f"{size_info['index']}")
            table.add_row("Metadata", f"{size_info['metadata']}")
            table.add_row("Total", f"{size_info['total']}", style="bold")
            
            console.print(table)
        else:
            # Simple output
            console.print(f"Vector Database Size: {size_info['total']} MB")
            
    except Exception as e:
        logger.error(f"Error getting vector database size: {str(e)}")
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.group()
def chat():
    """Chat with your OpenAPI specifications."""
    pass

@chat.command(name="ask")
@click.argument("question")
@click.option("--show-context", is_flag=True, help="Show the context used for the answer")
def ask(question: str, show_context: bool):
    """Ask a single question."""
    async def _ask():
        try:
            from app.services.rag_service import RAGService
            from app.services.openrouter_service import OpenRouterService
            
            # Initialize services
            rag_service = RAGService(vector_service, OpenRouterService())
            
            try:
                # Get response with context if requested
                if show_context:
                    response_gen, context = await rag_service.get_response_with_context(question)
                    
                    # Show context first
                    console.print("\n[bold blue]Context used:[/bold blue]")
                    for ctx in context:
                        console.print(Panel(ctx, border_style="blue"))
                    console.print()
                    
                    # Show response with live updating
                    console.print("\n[bold green]Response:[/bold green]")
                    buffer = []
                    with console.status("[bold]Generating response...[/bold]"):
                        async for chunk in response_gen:
                            buffer.append(chunk)
                            # Clear line and print updated markdown
                            print("\033[2K\033[G", end="")  # Clear current line
                            console.print(Markdown("".join(buffer)), soft_wrap=True)
                else:
                    # Show response with live updating
                    console.print("\n[bold green]Response:[/bold green]")
                    buffer = []
                    with console.status("[bold]Generating response...[/bold]"):
                        async for chunk in rag_service.generate_response(question):
                            buffer.append(chunk)
                            # Clear line and print updated markdown
                            print("\033[2K\033[G", end="")  # Clear current line
                            console.print(Markdown("".join(buffer)), soft_wrap=True)
                    
            except Exception as e:
                console.print(f"\n[red]Error generating response: {str(e)}[/red]")

        except Exception as e:
            console.print(f"[red]Error starting chat session: {str(e)}[/red]")
            sys.exit(1)

    return run_async(_ask())

@chat.command(name="interactive")
@click.option("--show-context", is_flag=True, help="Show the context used for answers")
def interactive(show_context: bool):
    """Start an interactive chat session."""
    async def _interactive():
        try:
            from app.services.rag_service import RAGService
            from app.services.openrouter_service import OpenRouterService
            
            # Initialize services
            rag_service = RAGService(vector_service, OpenRouterService())
            
            console.print("[bold]Starting chat session. Type 'exit' to quit.[/bold]")
            
            while True:
                # Get user input
                query = click.prompt("\nYou")
                
                if query.lower() in ['exit', 'quit']:
                    break

                if not query.strip():
                    continue

                try:
                    # Get response with context if requested
                    if show_context:
                        response_gen, context = await rag_service.get_response_with_context(query)
                        
                        # Show context first
                        console.print("\n[bold blue]Context used:[/bold blue]")
                        for ctx in context:
                            console.print(Panel(ctx, border_style="blue"))
                        console.print()
                        
                        # Show response with live updating
                        console.print("\n[bold green]Response:[/bold green]")
                        buffer = []
                        with console.status("[bold]Generating response...[/bold]"):
                            async for chunk in response_gen:
                                buffer.append(chunk)
                                # Clear line and print updated markdown
                                print("\033[2K\033[G", end="")  # Clear current line
                                console.print(Markdown("".join(buffer)), soft_wrap=True)
                    else:
                        # Show response with live updating
                        console.print("\n[bold green]Response:[/bold green]")
                        buffer = []
                        with console.status("[bold]Generating response...[/bold]"):
                            async for chunk in rag_service.generate_response(query):
                                buffer.append(chunk)
                                # Clear line and print updated markdown
                                print("\033[2K\033[G", end="")  # Clear current line
                                console.print(Markdown("".join(buffer)), soft_wrap=True)
                        
                except Exception as e:
                    console.print(f"[red]Error: {str(e)}[/red]")

        except Exception as e:
            console.print(f"[red]Error starting chat session: {str(e)}[/red]")
            sys.exit(1)

    return run_async(_interactive())

if __name__ == '__main__':
    cli()
