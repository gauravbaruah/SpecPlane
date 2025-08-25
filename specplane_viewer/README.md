# SpecPlane Viewer

Convert SpecPlane YAML specifications to Markdown and serve them via Docusaurus with full-text search capabilities.

## Features

- **YAML to Markdown Conversion**: Automatically convert SpecPlane YAML files to well-formatted Markdown
- **Docusaurus Integration**: Serve documentation with a modern, responsive web interface
- **Lunr Search**: Full-text search across all specifications (using docusaurus-lunr-search)
- **File Watching**: Real-time conversion when YAML files change
- **Mermaid Diagrams**: Render diagrams from markdown with proper syntax highlighting
- **Cross-References**: Handle references and cross-linking between specifications

## Installation

### Prerequisites

- Node.js 18.0 or higher
- npm or yarn package manager

### Install Dependencies

```bash
cd specplane_viewer
npm install
```

### Make CLI Executable

```bash
chmod +x bin/specplane
```

## Usage

### Basic Commands

#### Serve Command (Main Functionality)
```bash
# Convert specs and serve via Docusaurus
./bin/specplane serve ./specs

# With custom port
./bin/specplane serve ./specs --port 3001

# Watch for file changes
./bin/specplane serve ./specs --watch

# Auto-open browser
./bin/specplane serve ./specs --open
```

#### Convert Command (Just Convert)
```bash
# Convert specs to markdown without serving
./bin/specplane convert ./specs

# Custom output directory
./bin/specplane convert ./specs --output ./docs
```

#### Setup Command (Just Setup Docusaurus)
```bash
# Setup Docusaurus for existing markdown
./bin/specplane setup ./.specplane
```

### Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--port <port>` | Port number for Docusaurus server | 3001 |
| `--watch` | Watch for file changes | false |
| `--open` | Auto-open browser | false |
| `--input <path>` | Input directory containing YAML specs | ./specs |
| `--output <path>` | Output directory for markdown | ./.specplane/specs_viewer/docs |

## Project Structure

```
specplane_viewer/
├── bin/
│   └── specplane              # CLI executable
├── src/
│   ├── cli/
│   │   └── cli-interface.js   # Main CLI orchestration
│   ├── converter/
│   │   ├── spec2md-converter.js # YAML to Markdown conversion
│   │   ├── yaml-parser.js     # YAML parsing and validation
│   │   └── markdown-generator.js # Markdown generation
│   ├── docusaurus/
│   │   └── docusaurus-handler.js # Combined Docusaurus project management
│   ├── file-watcher/
│   │   └── file-watcher.js    # File system monitoring
│   └── utils/
│       └── logger.js          # Logging utility
├── config/                     # Configuration files
├── templates/                  # Template files
├── package.json               # Dependencies and scripts
└── README.md                  # This file
```

## Architecture

The SpecPlane Viewer follows the container/component architecture specified in our SpecPlane specifications:

### Containers
- **`cli_interface`**: Orchestrates the entire workflow
- **`spec2md_converter`**: Handles YAML to Markdown conversion
- **`docusaurus_handler`**: Manages Docusaurus project creation and execution

### Components
- **`yaml_parser`**: Parses and validates SpecPlane YAML
- **`markdown_generator`**: Generates formatted Markdown with proper sections
- **`file_watcher`**: Monitors directory changes
- **`dependency_checker`**: Validates required dependencies

## Development Workflow

### 1. File Watching
- Monitors `specs/` directory for changes
- 2-second debouncing to handle rapid file changes
- Automatically triggers conversion and rebuild

### 2. YAML Processing
- Parses SpecPlane YAML files with validation
- Generates structured Markdown with proper sections
- Maintains directory structure in output

### 3. Docusaurus Integration
- Creates/updates Docusaurus project configuration
- Installs lunr search plugin automatically
- Manages development and production builds

## Testing

### Manual Testing Commands

#### Test Basic Conversion
```bash
# Create a test specs directory
mkdir -p test_specs
echo "meta:\n  purpose: 'Test specification'\n  type: 'component'\n  level: 'component'" > test_specs/test.yaml

# Test conversion
./bin/specplane convert test_specs

# Convert with explicit input and output paths
./bin/specplane convert --input ./my_specs --output ./custom_output

# Convert using only flags (no positional arguments)
./bin/specplane convert --input ./specs --output ./.specplane/specs_viewer/docs

# Check output
ls -la .specplane/specs_viewer/docs/
```

### Server Control Commands

```bash
# Start Docusaurus server
./bin/specplane start --port 3001

# Stop Docusaurus server
./bin/specplane stop

# Check server status
./bin/specplane status
```

#### Test Full Workflow
```bash
# Start the full viewer
./bin/specplane serve test_specs --watch

# In another terminal, modify a YAML file
echo "  domain: 'test'" >> test_specs/test.yaml

# Watch the conversion and rebuild process
```

#### Test Docusaurus Setup
```bash
# Just setup Docusaurus
./bin/specplane setup ./.specplane

# Check generated files
ls -la
cat docusaurus.config.js
```

### Expected Behavior

1. **Conversion**: YAML files should be converted to Markdown with proper sections
2. **File Watching**: Changes should trigger automatic conversion and rebuild
3. **Dependencies**: Missing dependencies should be reported with helpful guidance
4. **Lunr Plugin**: Should be automatically installed and configured
5. **Server**: Docusaurus should start and serve the documentation

## Configuration

### Docusaurus Configuration

The viewer automatically generates a `docusaurus.config.js` with:
- Classic preset for documentation
- Lunr search plugin configuration
- Custom CSS for SpecPlane styling
- Responsive navigation and footer

### Markdown Structure

Generated Markdown follows this order:
1. **Meta Information** - Purpose, type, level, etc.
2. **System Relationships** - Mermaid diagram showing dependencies
3. **Diagrams** - All embedded Mermaid diagrams
4. **Contracts** - Capabilities, APIs, events, states
5. **Validation** - Acceptance criteria, edge cases, assumptions
6. **Other Sections** - Dependencies, constraints, etc.
7. **References** - External links and resources
8. **Table of Contents** - Navigation with up to level-2 headings

## Troubleshooting

### Common Issues

#### Missing Dependencies
```bash
# Check Node.js version
node --version  # Should be >= 18.0

# Check npm
npm --version

# Check Docusaurus CLI
npx docusaurus --version
```

#### Port Conflicts
```bash
# Use different port
./bin/specplane serve ./specs --port 3002
```

#### File Permissions
```bash
# Make CLI executable
chmod +x bin/specplane

# Check file permissions
ls -la bin/specplane
```

#### Docusaurus Build Issues
```bash
# Clear Docusaurus cache
cd .specplane
npx docusaurus clear

# Reinstall dependencies
npm install
```

### Logs

All operations are logged to `specplane-viewer.log` in JSONL format:
```bash
# View logs
tail -f specplane-viewer.log

# Clear logs
rm specplane-viewer.log
```

## Development

### Adding New Features

1. **New Commands**: Add to `bin/specplane` and `src/cli/cli-interface.js`
2. **New Components**: Create in appropriate container directory
3. **New Validations**: Extend `src/converter/yaml-parser.js`
4. **New Markdown Sections**: Extend `src/converter/markdown-generator.js`

### Testing Changes

```bash
# Development mode with auto-restart
npm run dev

# Run specific component
node src/converter/yaml-parser.js

# Test CLI
./bin/specplane --help
```

## Contributing

1. Follow the SpecPlane architecture specifications
2. Add comprehensive logging for all operations
3. Handle errors gracefully with helpful user messages
4. Maintain cross-platform compatibility
5. Add tests for new functionality

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: GitHub Issues
- **Documentation**: SpecPlane specifications in `../specs/`
- **Architecture**: Container/component specifications in `../specs/`
