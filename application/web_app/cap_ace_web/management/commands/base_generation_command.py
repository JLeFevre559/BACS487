"""
Base command class for AI content generation.
"""
from typing import List, Dict, Any, Optional
import json
import time
import random

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from .ai_utils import get_openai_response, get_claude_response, extract_json_from_response


class BaseGenerationCommand(BaseCommand):
    """Base command class for generating educational content with AI."""
    help = 'Generate educational content using AI'
    
    # Subclasses should override these attributes
    content_type_name = "content"  # e.g., "multiple choice questions"
    default_batch_size = 5
    system_message = "You are a financial education expert."
    
    def add_arguments(self, parser):
        """Add common command line arguments."""
        parser.add_argument(
            '--batch', 
            type=int, 
            default=self.default_batch_size,
            help=f'Number of {self.content_type_name} to generate in each batch'
        )
        parser.add_argument(
            '--no-input', 
            action='store_true',
            help='Skip user confirmation for each batch'
        )
        parser.add_argument(
            '--max', 
            type=int, 
            default=1,
            help='Maximum number of batches to generate'
        )
        parser.add_argument(
            '--dry-run', 
            action='store_true',
            help=f'Generate {self.content_type_name} but do not add them to the database'
        )
        parser.add_argument(
            '--ai', 
            type=str, 
            choices=['openai', 'claude'],
            default='openai',
            help='AI provider to use for generating content'
        )
        
        # Add model-specific arguments (to be implemented by subclasses)
        self.add_model_arguments(parser)
    
    def add_model_arguments(self, parser):
        """Add model-specific arguments. To be implemented by subclasses."""
        pass
    
    def format_prompt(self, batch_size: int, **kwargs) -> str:
        """Format the AI prompt with given parameters. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement format_prompt")
    
    def parse_response(self, response: str, batch_size: int) -> List[Dict[str, Any]]:
        """
        Parse and validate the JSON response from the AI.
        To be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement parse_response")
    
    def display_content(self, content_items: List[Dict[str, Any]]) -> None:
        """
        Display the generated content items to the user.
        To be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement display_content")
    
    def add_to_database(self, content_items: List[Dict[str, Any]]) -> int:
        """
        Add content items to the database.
        To be implemented by subclasses.
        
        Returns:
            Number of items successfully added
        """
        raise NotImplementedError("Subclasses must implement add_to_database")
    
    def get_user_confirmation(self) -> List[int]:
        """
        Get user confirmation for the batch of content.
        
        Returns:
            List of indices to reject, or "all" to reject all
        """
        while True:
            self.stdout.write(f"\nEnter {self.content_type_name} numbers to reject (e.g., '1, 3, 5'), 'all' to reject all, or press Enter to accept all: ")
            user_input = input().strip().lower()
            
            if not user_input:
                return []  # Accept all
                
            if user_input == 'all':
                return "all"  # Reject all
                
            try:
                # Parse the input as a list of numbers
                rejected = []
                for part in user_input.split(','):
                    # Handle formats like "1" or "reject 1"
                    num_str = part.strip().replace('reject', '').strip()
                    if num_str:
                        rejected.append(int(num_str))
                return rejected
            except ValueError:
                self.stdout.write(self.style.ERROR("Invalid input. Please enter numbers separated by commas."))
    
    def handle(self, *args, **options):
        """Main command execution."""
        batch_size = options['batch']
        no_input = options['no_input']
        max_batches = options['max']
        dry_run = options['dry_run']
        ai_provider = options['ai']
        
        total_added = 0
        total_generated = 0
        
        for batch in range(1, max_batches + 1):
            self.stdout.write("-" * 50)
            self.stdout.write(self.style.SUCCESS(f"Generating batch {batch}/{max_batches}..."))
            
            # Always use random for each API call if no category specified
            # We pass in the original options to let each content item pick its own random category
            prompt_params = self.process_options(options, use_random=True)
            
            # Display summary of what we're about to do for this batch
            self.display_generation_summary(batch_size, 1, ai_provider, prompt_params, dry_run)
            
            # Format the prompt with the current batch information
            prompt = self.format_prompt(batch_size, **prompt_params)
            
            # Get response from selected AI provider
            try:
                if ai_provider == 'openai':
                    response = get_openai_response(prompt, self.system_message)
                else:  # claude
                    response = get_claude_response(prompt, self.system_message)
                    
                # Parse the response with the expected batch size
                content_items = self.parse_response(response, batch_size)
                total_generated += len(content_items)
                
                self.stdout.write(self.style.SUCCESS(f"Generated {len(content_items)} {self.content_type_name}"))
                
                # Output content and get user confirmation if needed
                if not no_input:
                    self.display_content(content_items)
                    rejected_indices = self.get_user_confirmation()
                    
                    if rejected_indices == "all":
                        self.stdout.write(self.style.WARNING(f"Rejected all {self.content_type_name} in this batch"))
                        continue
                    
                    # Remove rejected content
                    content_items = [item for i, item in enumerate(content_items, 1) if i not in rejected_indices]
                    
                # Add content to database
                if not dry_run:
                    added = self.add_to_database(content_items)
                    total_added += added
                    self.stdout.write(self.style.SUCCESS(f"Added {added} {self.content_type_name} to the database"))
                else:
                    self.stdout.write(self.style.WARNING(f"DRY RUN: {self.content_type_name.capitalize()} not added to database"))
                    
                # Add a small delay between batches to respect API rate limits
                if batch < max_batches:
                    time.sleep(2)
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error in batch {batch}: {str(e)}"))
                continue
                
        # Output final summary
        self.stdout.write("=" * 50)
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry run complete. Generated {total_generated} {self.content_type_name}."))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Generation complete. Added {total_added}/{total_generated} {self.content_type_name} to the database."
                )
            )
    
    def process_options(self, options: Dict[str, Any], use_random: bool = False) -> Dict[str, Any]:
        """
        Process command options and return parameters for prompt formatting.
        To be implemented by subclasses.
        
        Args:
            options: Command-line options
            use_random: If True, consider using random values for options not explicitly provided
            
        Returns:
            Dictionary of parameters for prompt formatting
        """
        raise NotImplementedError("Subclasses must implement process_options")
    
    def display_generation_summary(self, batch_size: int, max_batches: int, 
                                  ai_provider: str, prompt_params: Dict[str, Any],
                                  dry_run: bool) -> None:
        """
        Display a summary of what will be generated.
        To be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement display_generation_summary")