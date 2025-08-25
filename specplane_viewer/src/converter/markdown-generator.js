/**
 * Markdown Generator Component
 * Generates well-formatted Markdown from parsed SpecPlane data
 */

const { Logger } = require('../utils/logger');

class MarkdownGenerator {
  constructor() {
    this.logger = new Logger();
    this.stats = {
      filesGenerated: 0,
      sectionsGenerated: 0,
      diagramsRendered: 0,
      referencesProcessed: 0
    };
  }

  /**
   * Generate complete markdown from SpecPlane data
   */
  async generateMarkdown(specData) {
    try {
      this.logger.debug('Generating markdown for specification');
      
      // Generate frontmatter for Docusaurus routing
      const frontmatter = this.generateFrontmatter(specData.meta);
      
      const sections = [];
      
      // 1. Meta section (first)
      if (specData.meta) {
        sections.push(this.generateMetaSection(specData.meta));
      }
      
      // 2. Relationship diagram (immediately after meta)
      if (specData.relationships || specData.dependencies) {
        sections.push(this.generateRelationshipDiagram(specData));
      }
      
      // 3. Diagrams section
      if (specData.diagrams && specData.diagrams.length > 0) {
        sections.push(this.generateDiagramsSection(specData.diagrams));
      }
      
      // 4. Contracts section
      if (specData.contracts) {
        sections.push(this.generateContractsSection(specData.contracts));
      }
      
      // 5. Validation section
      if (specData.validation) {
        sections.push(this.generateValidationSection(specData.validation));
      }
      
      // 6. Other sections (dependencies, constraints, etc.)
      sections.push(this.generateOtherSections(specData));
      
      // 7. References section
      if (specData.refs) {
        sections.push(this.generateReferencesSection(specData.refs));
      }
      
      // 8. Table of contents
      sections.push(this.generateTableOfContents(sections));
      
      // Combine all sections
      const markdown = sections.join('\n\n');
      
      // Add frontmatter at the beginning
      const finalMarkdown = frontmatter + '\n\n' + markdown;
      
      this.stats.filesGenerated++;
      this.stats.sectionsGenerated += sections.length;
      
      this.logger.debug(`Markdown generated with ${sections.length} sections`);
      
      return finalMarkdown;
      
    } catch (error) {
      this.logger.error('Failed to generate markdown:', error);
      throw error;
    }
  }

  /**
   * Generate frontmatter for Docusaurus routing
   */
  generateFrontmatter(meta) {
    if (!meta) return '';
    
    const frontmatter = {
      id: meta.id || 'untitled',
      title: meta.purpose || 'Specification',
      sidebar_label: meta.id || meta.purpose || 'Specification',
      description: meta.purpose || 'SpecPlane specification',
      keywords: [...new Set([meta.type, meta.level, meta.domain].filter(Boolean))],
      hide_table_of_contents: false,
      toc_min_heading_level: 2,
      toc_max_heading_level: 3
    };
    
    // Convert to YAML frontmatter
    const yaml = require('js-yaml');
    return '---\n' + yaml.dump(frontmatter) + '---';
  }

  /**
   * Generate meta section
   */
  generateMetaSection(meta) {
    let markdown = '# Meta Information\n\n';
    
    if (meta.purpose) {
      markdown += `**Purpose:** ${meta.purpose}\n\n`;
    }
    
    if (meta.type) {
      markdown += `**Type:** ${meta.type}\n\n`;
    }
    
    if (meta.level) {
      markdown += `**Level:** ${meta.level}\n\n`;
    }
    
    if (meta.domain) {
      markdown += `**Domain:** ${meta.domain}\n\n`;
    }
    
    if (meta.status) {
      markdown += `**Status:** ${meta.status}\n\n`;
    }
    
    if (meta.version) {
      markdown += `**Version:** ${meta.version}\n\n`;
    }
    
    if (meta.id) {
      markdown += `**ID:** ${meta.id}\n\n`;
    }
    
    if (meta.owner) {
      markdown += `**Owner:** ${meta.owner}\n\n`;
    }
    
    if (meta.last_updated) {
      markdown += `**Last Updated:** ${meta.last_updated}\n\n`;
    }
    
    return markdown.trim();
  }

  /**
   * Generate relationship diagram
   */
  generateRelationshipDiagram(specData) {
    let markdown = '# System Relationships\n\n';
    
    // Create a simple graph showing relationships
    const relationships = [];
    
    if (specData.relationships) {
      if (specData.relationships.depends_on) {
        relationships.push(...specData.relationships.depends_on.map(dep => `  ${specData.meta?.id || 'this'} --> ${dep}`));
      }
      
      if (specData.relationships.used_by) {
        relationships.push(...specData.relationships.used_by.map(user => `  ${user} --> ${specData.meta?.id || 'this'}`));
      }
      
      if (specData.relationships.integrates_with) {
        relationships.push(...specData.relationships.integrates_with.map(integration => `  ${specData.meta?.id || 'this'} -.-> ${integration}`));
      }
    }
    
    if (relationships.length > 0) {
      markdown += '```mermaid\ngraph TD\n';
      markdown += relationships.join('\n');
      markdown += '\n```\n\n';
    } else {
      markdown += '*No relationships defined*\n\n';
    }
    
    return markdown;
  }

  /**
   * Generate diagrams section
   */
  generateDiagramsSection(diagrams) {
    let markdown = '# Diagrams\n\n';
    
    for (const diagram of diagrams) {
      if (diagram.title) {
        markdown += `## ${diagram.title}\n\n`;
      }
      
      if (diagram.description) {
        markdown += `${diagram.description}\n\n`;
      }
      
      if (diagram.mermaid) {
        markdown += '```mermaid\n';
        markdown += diagram.mermaid;
        markdown += '\n```\n\n';
        this.stats.diagramsRendered++;
      }
    }
    
    return markdown.trim();
  }

  /**
   * Generate contracts section
   */
  generateContractsSection(contracts) {
    let markdown = '# Contracts\n\n';
    
    if (contracts.capabilities && contracts.capabilities.length > 0) {
      markdown += '## Capabilities\n\n';
      for (const capability of contracts.capabilities) {
        markdown += `- ${capability}\n`;
      }
      markdown += '\n';
    }
    
    if (contracts.apis && contracts.apis.length > 0) {
      markdown += '## APIs\n\n';
      for (const api of contracts.apis) {
        markdown += `- ${api}\n`;
      }
      markdown += '\n';
    }
    
    if (contracts.events && contracts.events.length > 0) {
      markdown += '## Events\n\n';
      for (const event of contracts.events) {
        markdown += `- ${event}\n`;
      }
      markdown += '\n';
    }
    
    if (contracts.states && contracts.states.length > 0) {
      markdown += '## States\n\n';
      for (const state of contracts.states) {
        markdown += `- ${state}\n`;
      }
      markdown += '\n';
    }
    
    return markdown.trim();
  }

  /**
   * Generate validation section
   */
  generateValidationSection(validation) {
    let markdown = '# Validation\n\n';
    
    if (validation.acceptance_criteria && validation.acceptance_criteria.length > 0) {
      markdown += '## Acceptance Criteria\n\n';
      for (const criteria of validation.acceptance_criteria) {
        markdown += `- [ ] ${criteria}\n`;
      }
      markdown += '\n';
    }
    
    if (validation.edge_cases && validation.edge_cases.length > 0) {
      markdown += '## Edge Cases\n\n';
      for (const edgeCase of validation.edge_cases) {
        markdown += `- ${edgeCase}\n`;
      }
      markdown += '\n';
    }
    
    if (validation.assumptions && validation.assumptions.length > 0) {
      markdown += '## Assumptions\n\n';
      for (const assumption of validation.assumptions) {
        markdown += `- ${assumption}\n`;
      }
      markdown += '\n';
    }
    
    if (validation.open_questions && validation.open_questions.length > 0) {
      markdown += '## Open Questions\n\n';
      for (const question of validation.open_questions) {
        markdown += `- ${question}\n`;
      }
      markdown += '\n';
    }
    
    return markdown.trim();
  }

  /**
   * Generate other sections
   */
  generateOtherSections(specData) {
    let markdown = '';
    
    if (specData.dependencies) {
      markdown += '## Dependencies\n\n';
      
      if (specData.dependencies.internal && specData.dependencies.internal.length > 0) {
        markdown += '### Internal Dependencies\n\n';
        for (const dep of specData.dependencies.internal) {
          markdown += `- ${dep}\n`;
        }
        markdown += '\n';
      }
      
      if (specData.dependencies.external && specData.dependencies.external.length > 0) {
        markdown += '### External Dependencies\n\n';
        for (const dep of specData.dependencies.external) {
          markdown += `- ${dep}\n`;
        }
        markdown += '\n';
      }
    }
    
    if (specData.constraints) {
      markdown += '## Constraints\n\n';
      
      if (specData.constraints.performance) {
        markdown += '### Performance\n\n';
        for (const [key, value] of Object.entries(specData.constraints.performance)) {
          markdown += `- **${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:** ${value}\n`;
        }
        markdown += '\n';
      }
      
      if (specData.constraints.security_privacy) {
        markdown += '### Security & Privacy\n\n';
        for (const [key, value] of Object.entries(specData.constraints.security_privacy)) {
          markdown += `- **${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:** ${value}\n`;
        }
        markdown += '\n';
      }
    }
    
    return markdown.trim();
  }

  /**
   * Generate references section
   */
  generateReferencesSection(refs) {
    let markdown = '# References\n\n';
    
    for (const [refId, ref] of Object.entries(refs)) {
      markdown += `## ${ref.title || refId}\n\n`;
      
      if (ref.type) {
        markdown += `**Type:** ${ref.type}\n\n`;
      }
      
      if (ref.url) {
        markdown += `**URL:** [${ref.url}](${ref.url})\n\n`;
      }
      
      if (ref.path) {
        markdown += `**Path:** ${ref.path}\n\n`;
      }
      
      if (ref.version) {
        markdown += `**Version:** ${ref.version}\n\n`;
      }
      
      if (ref.owner) {
        markdown += `**Owner:** ${ref.owner}\n\n`;
      }
      
      if (ref.tags && ref.tags.length > 0) {
        markdown += `**Tags:** ${ref.tags.join(', ')}\n\n`;
      }
      
      if (ref.notes) {
        markdown += `${ref.notes}\n\n`;
      }
      
      markdown += '---\n\n';
      this.stats.referencesProcessed++;
    }
    
    return markdown.trim();
  }

  /**
   * Generate table of contents
   */
  generateTableOfContents(sections) {
    let markdown = '# Table of Contents\n\n';
    
    // Extract headings from sections (up to level 2)
    const headings = [];
    
    for (const section of sections) {
      const lines = section.split('\n');
      for (const line of lines) {
        if (line.startsWith('# ')) {
          headings.push(`- [${line.substring(2)}](#${line.substring(2).toLowerCase().replace(/[^a-z0-9]+/g, '-')})`);
        } else if (line.startsWith('## ')) {
          headings.push(`  - [${line.substring(3)}](#${line.substring(3).toLowerCase().replace(/[^a-z0-9]+/g, '-')})`);
        }
      }
    }
    
    if (headings.length > 0) {
      markdown += headings.join('\n');
    } else {
      markdown += '*No headings found*';
    }
    
    return markdown;
  }

  /**
   * Get generation statistics
   */
  getStats() {
    return { ...this.stats };
  }

  /**
   * Reset statistics
   */
  resetStats() {
    this.stats = {
      filesGenerated: 0,
      sectionsGenerated: 0,
      diagramsRendered: 0,
      referencesProcessed: 0
    };
  }
}

module.exports = { MarkdownGenerator };
