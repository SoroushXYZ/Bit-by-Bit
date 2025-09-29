"""
Grid placement algorithm for component layout generation.
Implements retry-based placement with stocks and bits filling.
"""

import json
import numpy as np
import random
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Union
from dataclasses import dataclass
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader


@dataclass
class Component:
    name: str
    width: int
    height: int
    count: int
    can_rotate: bool
    priority: int
    
    def __post_init__(self):
        self.instances = []
        for i in range(self.count):
            self.instances.append({
                'id': f"{self.name}_{i+1}",
                'width': self.width,
                'height': self.height,
                'placed': False,
                'position': None
            })


@dataclass
class FlexibleComponent:
    name: str
    shapes: List[Dict[str, int]]
    total_count: int
    can_rotate: bool
    priority: int


@dataclass
class Placement:
    component_id: str
    x: int
    y: int
    width: int
    height: int
    component_type: str
    data: Optional[Dict] = None


class RetryGridPlacer:
    """Grid placer with retry algorithm for component placement."""
    
    def __init__(self, grid_width: int, grid_height: int):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = np.zeros((grid_height, grid_width), dtype=int)
        self.placements = []
        
    def can_place(self, x: int, y: int, width: int, height: int) -> bool:
        """Check if a component can be placed at the given position"""
        if x + width > self.grid_width or y + height > self.grid_height:
            return False
        if x < 0 or y < 0:
            return False
            
        # Check if the area is free
        return np.all(self.grid[y:y+height, x:x+width] == 0)
    
    def place_component(self, component_id: str, x: int, y: int, width: int, height: int, 
                       component_type: str, data: Optional[Dict] = None) -> bool:
        """Place a component at the given position"""
        if not self.can_place(x, y, width, height):
            return False
            
        # Mark the grid cells as occupied
        self.grid[y:y+height, x:x+width] = 1
        
        # Add to placements
        self.placements.append(Placement(component_id, x, y, width, height, component_type, data))
        return True
    
    def get_available_positions(self, width: int, height: int) -> List[Tuple[int, int]]:
        """Get all available positions for a component of given size"""
        positions = []
        for y in range(self.grid_height - height + 1):
            for x in range(self.grid_width - width + 1):
                if self.can_place(x, y, width, height):
                    positions.append((x, y))
        return positions
    
    def get_random_position(self, width: int, height: int) -> Optional[Tuple[int, int]]:
        """Get a random available position"""
        positions = self.get_available_positions(width, height)
        return random.choice(positions) if positions else None
    
    def find_2x2_spaces(self) -> List[Tuple[int, int]]:
        """Find all available 2x2 spaces"""
        return self.get_available_positions(2, 2)
    
    def find_single_cells(self) -> List[Tuple[int, int]]:
        """Find all available single cells"""
        return self.get_available_positions(1, 1)
    
    def find_2x1_spaces(self) -> List[Tuple[int, int]]:
        """Find all available 2x1 spaces"""
        return self.get_available_positions(2, 1)


class GriddingProcessor:
    """Processes component placement and generates grid blueprint."""
    
    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader
        self.logger = get_logger()
        self.config = self.config_loader.get_step_config('gridding')
        self.data_paths = self.config_loader.get_data_paths()
        
        # Set random seed for reproducible results
        random.seed()
        self.logger.info("Gridding processor initialized with random seed")
    
    def _create_components(self) -> Tuple[List[Component], List[FlexibleComponent]]:
        """Create component objects from configuration."""
        components = []
        flexible_components = []
        
        for comp_config in self.config['components']:
            if 'shapes' in comp_config:
                # This is a flexible component
                flexible_component = FlexibleComponent(
                    name=comp_config['name'],
                    shapes=comp_config['shapes'],
                    total_count=comp_config['total_count'],
                    can_rotate=comp_config['can_rotate'],
                    priority=comp_config['priority']
                )
                flexible_components.append(flexible_component)
            else:
                # This is a fixed-size component
                component = Component(
                    name=comp_config['name'],
                    width=comp_config['width'],
                    height=comp_config['height'],
                    count=comp_config['count'],
                    can_rotate=comp_config['can_rotate'],
                    priority=comp_config['priority']
                )
                components.append(component)
        
        return components, flexible_components
    
    def _reset_all_components(self, components: List[Component], flexible_components: List[FlexibleComponent]):
        """Reset all component instances to unplaced state."""
        for component in components:
            for instance in component.instances:
                instance['placed'] = False
                instance['position'] = None
    
    def _load_fallback_layout(self) -> RetryGridPlacer:
        """Load fallback grid layout from file."""
        try:
            fallback_path = Path(__file__).parent / 'fallback_grid_blueprint.json'
            
            if not fallback_path.exists():
                self.logger.error(f"❌ Fallback layout file not found: {fallback_path}")
                # Create a minimal fallback
                return self._create_minimal_fallback()
            
            with open(fallback_path, 'r', encoding='utf-8') as f:
                fallback_data = json.load(f)
            
            # Create a placer with the fallback grid dimensions
            grid_config = fallback_data['metadata']['grid_config']
            placer = RetryGridPlacer(grid_config['columns'], grid_config['rows'])
            
            # Load all components from fallback
            for comp_data in fallback_data['components']:
                position = comp_data['position']
                placer.place_component(
                    comp_data['id'],
                    position['column'] - 1,  # Convert from 1-based to 0-based
                    position['row'] - 1,
                    position['width'],
                    position['height'],
                    comp_data['type'],
                    comp_data.get('data', {})
                )
            
            self.logger.info(f"✅ Loaded fallback layout with {len(placer.placements)} components")
            return placer
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load fallback layout: {e}")
            return self._create_minimal_fallback()
    
    def _create_minimal_fallback(self) -> RetryGridPlacer:
        """Create a minimal fallback layout if file loading fails."""
        self.logger.warning("🔄 Creating minimal fallback layout...")
        
        # Create a basic 12x16 grid
        placer = RetryGridPlacer(12, 16)
        
        # Place a few basic components
        try:
            # Place one branding
            placer.place_component("branding_1", 0, 0, 2, 2, 'branding')
            # Place one headline
            placer.place_component("headline_1", 2, 0, 5, 4, 'headline')
            # Place one quick link
            placer.place_component("quick_link_1", 0, 2, 6, 1, 'quick_link')
            
            self.logger.info("✅ Created minimal fallback layout")
        except Exception as e:
            self.logger.error(f"❌ Failed to create minimal fallback: {e}")
        
        return placer
    
    def _update_fallback_layout(self, blueprint: dict):
        """Update the fallback layout with a successful blueprint."""
        try:
            fallback_path = Path(__file__).parent / 'fallback_grid_blueprint.json'
            
            with open(fallback_path, 'w', encoding='utf-8') as f:
                json.dump(blueprint, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Updated fallback layout: {fallback_path}")
            
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to update fallback layout: {e}")
    
    def _retry_placement_algorithm(self, components: List[Component], flexible_components: List[FlexibleComponent], 
                                 grid_width: int, grid_height: int) -> RetryGridPlacer:
        """Retry algorithm: Keep trying until all components are placed, then add stocks and bits."""
        max_retries = self.config.get('max_retries', 500)
        self.logger.info(f"Starting retry algorithm (max {max_retries} attempts)...")
        
        for attempt in range(max_retries):
            self.logger.info(f"--- Attempt {attempt + 1} ---")
            
            # Reset all components for this attempt
            self._reset_all_components(components, flexible_components)
            
            # Create fresh placer for this attempt
            placer = RetryGridPlacer(grid_width, grid_height)
            
            # Separate brandings from other components
            branding_components = [c for c in components if c.name == 'branding']
            other_components = [c for c in components if c.name != 'branding']
            
            # Step 1: Place brandings randomly
            self.logger.info("Placing brandings randomly...")
            branding_success = True
            for component in branding_components:
                for instance in component.instances:
                    position = placer.get_random_position(instance['width'], instance['height'])
                    if position:
                        x, y = position
                        success = placer.place_component(
                            instance['id'], x, y, 
                            instance['width'], instance['height'], 
                            'branding'
                        )
                        if success:
                            instance['placed'] = True
                            instance['position'] = (x, y)
                            self.logger.info(f"  Placed {instance['id']} at ({x}, {y})")
                        else:
                            branding_success = False
                            break
                    else:
                        branding_success = False
                        break
                if not branding_success:
                    break
            
            if not branding_success:
                self.logger.info("  Failed to place all brandings, retrying...")
                continue
            
            # Step 2: Place remaining components randomly
            self.logger.info("Placing remaining components...")
            all_components = []
            
            # Add remaining fixed components
            for component in other_components:
                for instance in component.instances:
                    all_components.append({
                        'type': 'fixed',
                        'instance': instance,
                        'component': component
                    })
            
            # Add flexible components (randomly choose shapes)
            for flexible_component in flexible_components:
                shapes = flexible_component.shapes
                for i in range(flexible_component.total_count):
                    chosen_shape = random.choice(shapes)
                    all_components.append({
                        'type': 'flexible',
                        'instance': {
                            'id': f"{flexible_component.name}_{i+1}",
                            'width': chosen_shape['width'],
                            'height': chosen_shape['height'],
                            'placed': False,
                            'position': None
                        },
                        'component': flexible_component
                    })
            
            # Randomize order
            random.shuffle(all_components)
            
            # Try to place all components with multiple attempts per component
            all_placed = True
            for item in all_components:
                instance = item['instance']
                component = item['component']
                
                if instance['placed']:
                    continue
                
                # Try multiple random positions for this component
                placed_this_component = False
                for _ in range(10):  # Try up to 10 positions
                    position = placer.get_random_position(instance['width'], instance['height'])
                    if position:
                        x, y = position
                        success = placer.place_component(
                            instance['id'], x, y, 
                            instance['width'], instance['height'], 
                            instance.get('type', 'fixed')
                        )
                        if success:
                            instance['placed'] = True
                            instance['position'] = (x, y)
                            self.logger.info(f"  Placed {instance['id']} at ({x}, {y}) - {instance['width']}x{instance['height']}")
                            placed_this_component = True
                            break
                
                if not placed_this_component:
                    self.logger.info(f"  ❌ Could not place {instance['id']} after 10 attempts")
                    all_placed = False
                    break
            
            if all_placed:
                # Verify all components are actually placed
                total_required = sum(len(c.instances) for c in components) + sum(fc.total_count for fc in flexible_components)
                total_placed = len(placer.placements)
                
                self.logger.info(f"✅ Success! All components placed in {attempt + 1} attempts")
                self.logger.info(f"  Required: {total_required}, Placed: {total_placed}")
                break
            else:
                self.logger.info(f"  Failed to place all components, retrying...")
                continue
        else:
            self.logger.error(f"❌ Failed to place all components after {max_retries} attempts")
            self.logger.info("🔄 Using fallback grid layout...")
            return self._load_fallback_layout()
        
        # Final verification
        total_required = sum(len(c.instances) for c in components) + sum(fc.total_count for fc in flexible_components)
        total_placed = len(placer.placements)
        
        if total_placed < total_required:
            self.logger.warning(f"⚠️  Warning: Only placed {total_placed}/{total_required} required components")
            self.logger.info("Proceeding with stocks and bits anyway...")
        else:
            self.logger.info(f"✅ All {total_required} required components successfully placed!")
        
        # Step 3: Add stocks to available 2x2 spaces
        if self.config['stock_components']['enabled']:
            self.logger.info("Adding stocks to 2x2 spaces...")
            stock_spaces = placer.find_2x2_spaces()
            max_stocks = self.config['stock_components']['max_count']
            
            stocks_placed = 0
            for i, (x, y) in enumerate(stock_spaces):
                if stocks_placed >= max_stocks:
                    break
                
                success = placer.place_component(
                    f"stock_{i+1}", x, y, 2, 2, 
                    'stock', 
                    {
                        'symbol': f'STOCK_{i+1}',
                        'price': 0.0,
                        'change': 0.0,
                        'change_percent': 0.0
                    }
                )
                
                if success:
                    stocks_placed += 1
                    self.logger.info(f"  Placed stock placeholder at ({x}, {y})")
            
            self.logger.info(f"Placed {stocks_placed} stock placeholders")
        
        # Step 4: Add 1 day number component to 2x1 space
        if self.config['day_number_component']['enabled']:
            self.logger.info("Adding 1 day number component to 2x1 space...")
            day_spaces = placer.find_2x1_spaces()
            
            if day_spaces:
                # Use the first available 2x1 space
                x, y = day_spaces[0]
                success = placer.place_component(
                    "day_1", x, y, 2, 1, 
                    'dayNumber', 
                    {'day_number': 1}
                )
                
                if success:
                    self.logger.info(f"  Placed day number placeholder at ({x}, {y})")
                else:
                    self.logger.info("  Failed to place day number")
            else:
                self.logger.info("  No 2x1 spaces available for day number")
        
        # Step 5: Fill remaining single cells with bits
        if self.config['bit_components']['enabled']:
            self.logger.info("Filling remaining cells with bits...")
            single_cells = placer.find_single_cells()
            bits_placed = 0
            
            for i, (x, y) in enumerate(single_cells):
                bit_value = random.randint(0, 1)
                
                success = placer.place_component(
                    f"bit_{i+1}", x, y, 1, 1, 
                    'bit', 
                    {'value': bit_value}
                )
                
                if success:
                    bits_placed += 1
            
            self.logger.info(f"Placed {bits_placed} bit placeholders")
        
        # Final summary
        total_cells = grid_width * grid_height
        occupied_cells = np.sum(placer.grid)
        efficiency = (occupied_cells / total_cells) * 100
        
        self.logger.info(f"📊 Final Summary:")
        self.logger.info(f"  Required components: {total_required}")
        self.logger.info(f"  Placed components: {len(placer.placements)}")
        self.logger.info(f"  Total efficiency: {efficiency:.1f}%")
        
        return placer
    
    def _export_to_blueprint_format(self, placer: RetryGridPlacer) -> dict:
        """Export the placement solution in blueprint format."""
        
        # Convert placements to blueprint format
        blueprint_components = []
        
        for placement in placer.placements:
            # Determine component type
            if 'headline' in placement.component_id:
                comp_type = 'headline'
            elif 'github_repo' in placement.component_id:
                comp_type = 'github_repo'
            elif 'branding' in placement.component_id:
                comp_type = 'branding'
            elif 'quick_link' in placement.component_id:
                comp_type = 'quick_link'
            elif placement.component_type == 'stock':
                comp_type = 'stock'
            elif placement.component_type == 'dayNumber':
                comp_type = 'day_number'
            elif placement.component_type == 'bit':
                comp_type = 'bit'
            else:
                comp_type = 'unknown'
            
            blueprint_component = {
                'id': placement.component_id,
                'type': comp_type,
                'position': {
                    'row': placement.y + 1,  # 1-based indexing
                    'column': placement.x + 1,
                    'width': placement.width,
                    'height': placement.height
                },
                'data': placement.data or {}
            }
            
            blueprint_components.append(blueprint_component)
        
        # Create the complete blueprint
        blueprint = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'grid_config': {
                    'columns': placer.grid_width,
                    'rows': placer.grid_height,
                    'cell_size': self.config['grid_config']['cell_size']
                },
                'total_components': len(blueprint_components),
                'efficiency': round((np.sum(placer.grid) / (placer.grid_width * placer.grid_height)) * 100, 1)
            },
            'components': blueprint_components
        }
        
        return blueprint
    
    def _save_blueprint(self, blueprint: dict) -> str:
        """Save blueprint to raw data folder."""
        try:
            # Create raw directory
            raw_dir = Path(self.data_paths['raw'])
            raw_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = self.config['output']['filename_template'].format(timestamp=timestamp)
            
            output_path = raw_dir / filename
            
            # Save blueprint
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(blueprint, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Grid blueprint saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save grid blueprint: {e}")
            return None
    
    def process(self) -> Dict[str, any]:
        """Process component placement and generate grid blueprint."""
        try:
            self.logger.info("🎯 Starting grid blueprint generation")
            
            # Get grid dimensions
            grid_width = self.config['grid_config']['columns']
            grid_height = self.config['grid_config']['rows']
            
            self.logger.info(f"Grid size: {grid_width}x{grid_height}")
            
            # Create components
            components, flexible_components = self._create_components()
            
            # Calculate total space needed
            total_space_needed = 0
            for component in components:
                space_per_component = component.width * component.height
                total_space = space_per_component * component.count
                total_space_needed += total_space
            
            for flexible_component in flexible_components:
                avg_space = sum(shape['width'] * shape['height'] for shape in flexible_component.shapes) / len(flexible_component.shapes)
                total_avg_space = avg_space * flexible_component.total_count
                total_space_needed += total_avg_space
            
            self.logger.info(f"Total space needed: {total_space_needed:.1f} cells")
            self.logger.info(f"Space available: {grid_width * grid_height} cells")
            
            # Run placement algorithm
            placer = self._retry_placement_algorithm(components, flexible_components, grid_width, grid_height)
            
            # Export to blueprint format
            blueprint = self._export_to_blueprint_format(placer)
            
            # Save blueprint
            output_file = self._save_blueprint(blueprint)
            
            if not output_file:
                return {
                    'success': False,
                    'error': 'Failed to save grid blueprint'
                }
            
            # Update fallback layout with this successful layout
            self._update_fallback_layout(blueprint)
            
            self.logger.info("✅ Grid blueprint generation completed successfully")
            
            return {
                'success': True,
                'blueprint_file': output_file,
                'total_components': len(placer.placements),
                'efficiency': blueprint['metadata']['efficiency'],
                'metadata': blueprint['metadata']
            }
            
        except Exception as e:
            self.logger.error(f"Grid blueprint generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
