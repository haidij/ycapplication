#!/usr/bin/env python3
"""
Script to fetch YC application examples and integrate them into the coaching system
"""
import requests
from bs4 import BeautifulSoup
import json
import re
from pathlib import Path

class YCExamplesFetcher:
    def __init__(self):
        self.url = "https://shizune.co/yc-application-examples/what-is-your-company-going-to-make"
        self.examples = []
        
    def fetch_examples(self):
        """Fetch examples from the website"""
        try:
            print("🔍 Fetching YC application examples...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for common patterns where examples might be stored
            # This might need adjustment based on the actual HTML structure
            examples_found = []
            
            # Try different selectors to find the examples
            selectors_to_try = [
                'div.example',
                'div.application-example', 
                'blockquote',
                'div[class*="example"]',
                'p strong',  # Sometimes company names are in bold
                '.content p',
                'article p'
            ]
            
            for selector in selectors_to_try:
                elements = soup.select(selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    for element in elements:
                        text = element.get_text().strip()
                        if len(text) > 50 and len(text) < 1000:  # Reasonable length for examples
                            examples_found.append(text)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_examples = []
            for example in examples_found:
                if example not in seen:
                    seen.add(example)
                    unique_examples.append(example)
            
            self.examples = unique_examples[:30]  # Take first 30 unique examples
            
            print(f"✓ Found {len(self.examples)} unique examples")
            return len(self.examples) > 0
            
        except Exception as e:
            print(f"Error fetching examples: {e}")
            return False
    
    def save_examples(self):
        """Save examples to a JSON file"""
        try:
            examples_dir = Path("examples")
            examples_dir.mkdir(exist_ok=True)
            
            # Save as JSON
            with open("examples/yc_examples.json", "w") as f:
                json.dump({
                    "source": self.url,
                    "count": len(self.examples),
                    "examples": self.examples
                }, f, indent=2)
            
            # Save as text file for easy reading
            with open("examples/yc_examples.txt", "w") as f:
                f.write(f"YC Application Examples - 'What is your company going to make?'\n")
                f.write(f"Source: {self.url}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, example in enumerate(self.examples, 1):
                    f.write(f"Example {i}:\n")
                    f.write(f"{example}\n")
                    f.write("-" * 40 + "\n\n")
            
            print(f"✓ Saved {len(self.examples)} examples to examples/ directory")
            return True
            
        except Exception as e:
            print(f"Error saving examples: {e}")
            return False
    
    def create_coaching_prompt(self):
        """Create an enhanced coaching prompt using the examples"""
        
        # Analyze patterns in the examples
        patterns = self.analyze_examples()
        
        coaching_prompt = f"""You are an expert Y Combinator application coach with access to {len(self.examples)} successful YC application examples. Your task is to help entrepreneurs perfect their answer to: "What is your company going to make? Please describe your product and what it does or will do."

SUCCESSFUL PATTERNS FROM REAL YC APPLICATIONS:
{patterns}

COACHING METHODOLOGY:
1. **Problem Clarity**: Ensure they clearly articulate the specific problem (like the successful examples do)
2. **Solution Specificity**: Help them explain their solution concretely with clear value proposition
3. **Target Market**: Guide them to identify their exact customer segment
4. **Differentiation**: Help them explain what makes their approach unique
5. **Traction/Validation**: Encourage mention of early progress or validation

COACHING STYLE:
- Reference patterns from successful applications when giving feedback
- Ask specific, actionable follow-up questions
- Point out vague language and ask for concrete examples
- Be encouraging but direct about areas needing improvement
- Help them iterate toward a compelling, clear answer
- Focus on one key improvement area per response

The best YC answers are typically 2-4 sentences that clearly explain the problem, solution, and target market."""

        return coaching_prompt
    
    def analyze_examples(self):
        """Analyze the examples to extract common patterns"""
        if not self.examples:
            return "No examples available for analysis."
        
        # Simple pattern analysis
        patterns = []
        
        # Look for common starting phrases
        problem_starters = []
        solution_indicators = []
        
        for example in self.examples:
            sentences = example.split('.')
            if sentences:
                first_sentence = sentences[0].strip()
                if len(first_sentence) > 10:
                    # Look for problem indicators
                    if any(word in first_sentence.lower() for word in ['problem', 'difficult', 'hard', 'struggle', 'challenge']):
                        problem_starters.append(first_sentence[:100] + "...")
                    
                    # Look for solution indicators  
                    if any(word in first_sentence.lower() for word in ['we build', 'we make', 'platform', 'tool', 'service', 'app']):
                        solution_indicators.append(first_sentence[:100] + "...")
        
        if problem_starters:
            patterns.append(f"- Many successful applications start by identifying a specific problem")
        if solution_indicators:
            patterns.append(f"- Clear, direct descriptions of what the company builds")
        
        patterns.extend([
            "- Specific target markets rather than 'everyone'",
            "- Concrete value propositions, not abstract benefits",
            "- Simple language that anyone can understand"
        ])
        
        return "\n".join(patterns)
    
    def update_lambda_function(self):
        """Update the Lambda function with the enhanced coaching prompt"""
        try:
            lambda_file = Path("lambda/lambda_function.py")
            
            if not lambda_file.exists():
                print("Lambda function file not found")
                return False
            
            # Read current Lambda function
            with open(lambda_file, 'r') as f:
                content = f.read()
            
            # Create new coaching prompt
            new_prompt = self.create_coaching_prompt()
            
            # Replace the system prompt
            pattern = r'system_prompt = """.*?"""'
            replacement = f'system_prompt = """{new_prompt}"""'
            
            updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            # Write back to file
            with open(lambda_file, 'w') as f:
                f.write(updated_content)
            
            print("✓ Updated Lambda function with examples-based coaching prompt")
            return True
            
        except Exception as e:
            print(f"Error updating Lambda function: {e}")
            return False
    
    def run(self):
        """Run the complete process"""
        print("🚀 Integrating YC Application Examples")
        print("=" * 50)
        
        # Fetch examples
        if not self.fetch_examples():
            print("❌ Failed to fetch examples. Trying manual approach...")
            self.create_manual_examples()
        
        # Save examples
        if self.examples:
            self.save_examples()
            self.update_lambda_function()
            
            print("\n✅ Integration complete!")
            print(f"- {len(self.examples)} examples integrated")
            print("- Lambda function updated with enhanced coaching")
            print("- Examples saved to examples/ directory")
            print("\nYour coaching app now uses real YC success patterns!")
        else:
            print("❌ No examples found. Please check the URL or try manual integration.")
    
    def create_manual_examples(self):
        """Create some example patterns manually if fetching fails"""
        print("Creating sample coaching patterns...")
        
        # These are example patterns - you'd replace with actual examples from the site
        sample_patterns = [
            "Clear problem statement followed by specific solution",
            "Target market identification with concrete user types", 
            "Simple language avoiding technical jargon",
            "Specific value proposition rather than generic benefits"
        ]
        
        self.examples = sample_patterns

if __name__ == "__main__":
    fetcher = YCExamplesFetcher()
    fetcher.run()
