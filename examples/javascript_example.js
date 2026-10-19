#!/usr/bin/env node
/**
 * Example JavaScript/Node.js client for the Markdown MCP server.
 * 
 * This script demonstrates how to connect to and use the Markdown MCP server
 * from a JavaScript/Node.js application. It shows basic usage patterns,
 * error handling, and various document processing examples.
 * 
 * Requirements:
 * - Node.js 18+ (for built-in fetch support)
 * - No additional dependencies
 * 
 * Usage:
 * node examples/javascript_example.js
 * 
 * @author MCP Server Examples
 * @version 1.0.0
 */

/**
 * Client for interacting with the Markdown MCP server.
 * 
 * Provides methods to split Markdown documents into hierarchical sections
 * with preserved parent-child relationships and sibling connections.
 * 
 * @class MarkdownMCPClient
 */
class MarkdownMCPClient {
    /**
     * Initialize the MCP client with server configuration.
     * 
     * @param {string} [baseUrl='http://localhost:8080'] - Base URL of the MCP server
     * @throws {Error} When baseUrl is invalid
     */
    constructor(baseUrl = 'http://localhost:8080') {
        if (!baseUrl || typeof baseUrl !== 'string') {
            throw new Error('Base URL must be a non-empty string');
        }
        
        try {
            new URL(baseUrl); // Validate URL format
        } catch (error) {
            throw new Error(`Invalid base URL format: ${baseUrl}`);
        }
        
        this.baseUrl = baseUrl;
        this.mcpUrl = `${baseUrl}/server/mcp/`;
    }

    /**
     * Split markdown text into hierarchical sections using the MCP server.
     * 
     * Processes the input Markdown text and returns an array of section objects
     * containing headers, content, hierarchy levels, and relationship metadata.
     * 
     * @param {string} text - The Markdown text to process (must contain headers with # symbols)
     * @param {Object} [options={}] - Optional configuration
     * @param {number} [options.timeout=30000] - Request timeout in milliseconds
     * @returns {Promise<Array<Object>>} Array of section objects with hierarchy information
     * @throws {Error} When text is invalid, server is unreachable, or response is malformed
     * 
     * @example
     * const sections = await client.splitText('# Title\nContent\n## Subtitle\nMore content');
     * console.log(sections[0].header); // 'Title'
     * console.log(sections[1].metadata.parents); // {h1: 'Title'}
     */
    async splitText(text, options = {}) {
        // Input validation
        if (!text) {
            throw new Error('Text parameter is required and cannot be empty');
        }
        
        if (typeof text !== 'string') {
            throw new Error('Text parameter must be a string');
        }
        
        if (text.trim().length === 0) {
            throw new Error('Text parameter cannot be only whitespace');
        }
        
        const { timeout = 30000 } = options;
        
        if (typeof timeout !== 'number' || timeout <= 0) {
            throw new Error('Timeout must be a positive number');
        }
        
        // Generate unique request ID
        const requestId = Date.now() + Math.random().toString(36).substring(2, 11);
        
        const payload = {
            jsonrpc: '2.0',
            id: requestId,
            method: 'tools/call',
            params: {
                name: 'split_text',
                arguments: { text }
            }
        };
        
        // Setup timeout handling
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            controller.abort();
        }, timeout);

        try {
            const response = await fetch(this.mcpUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json, text/event-stream'
                },
                body: JSON.stringify(payload),
                signal: controller.signal
            });

            if (!response.ok) {
                const errorText = await response.text().catch(() => 'Unknown error');
                throw new Error(`HTTP ${response.status} ${response.statusText}: ${errorText}`);
            }

            const responseText = await response.text();
            
            if (!responseText) {
                throw new Error('Received empty response from server');
            }
            
            // Parse SSE response
            if (responseText.startsWith('event: message') && responseText.includes('data: ')) {
                try {
                    // Extract data part from SSE format
                    const dataStart = responseText.indexOf('data: ') + 'data: '.length;
                    const dataPart = responseText.substring(dataStart);
                    const result = JSON.parse(dataPart);
                    
                    // Validate MCP response structure
                    if (!result.result || !result.result.content || !Array.isArray(result.result.content)) {
                        throw new Error('Invalid MCP response structure');
                    }
                    
                    // Extract the actual result from MCP response
                    const sectionsData = result.result.content[0].text;
                    
                    if (!sectionsData) {
                        throw new Error('No sections data in MCP response');
                    }
                    
                    // Parse the JSON string containing the sections
                    const sections = JSON.parse(sectionsData);
                    
                    // Validate sections format
                    const sectionsArray = Array.isArray(sections) ? sections : [sections];
                    
                    // Validate each section has required properties
                    for (const section of sectionsArray) {
                        if (typeof section.header !== 'string' || typeof section.content !== 'string' || !section.metadata) {
                            throw new Error(`Invalid section structure in response: missing required fields in section '${section.header || 'unknown'}'`);
                        }
                    }
                    
                    return sectionsArray;
                } catch (parseError) {
                    throw new Error(`Failed to parse SSE response: ${parseError.message}`);
                }
            } else {
                // Fallback for regular JSON response
                try {
                    const data = JSON.parse(responseText);
                    const result = data.result;
                    return Array.isArray(result) ? result : [result];
                } catch (parseError) {
                    throw new Error(`Failed to parse JSON response: ${parseError.message}`);
                }
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error(`Request timeout after ${timeout}ms`);
            }
            
            if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
                throw new Error(`Cannot connect to MCP server at ${this.mcpUrl}. Ensure the server is running.`);
            }
            
            // Re-throw our custom errors, wrap system errors
            if (error.message.startsWith('HTTP') || 
                error.message.startsWith('Text parameter') ||
                error.message.startsWith('Failed to parse') ||
                error.message.startsWith('Request timeout') ||
                error.message.startsWith('Cannot connect')) {
                throw error;
            }
            
            throw new Error(`MCP client error: ${error.message}`);
        } finally {
            clearTimeout(timeoutId);
        }
    }
}

/**
 * Group section headers by their parent section id.
 *
 * @param {Array<Object>} sections - Sections returned by splitText
 * @returns {Map<(number|null), string[]>} Map from metadata.parent_id (null = top level) to child headers
 */
function groupHeadersByParent(sections) {
    const childrenByParent = new Map();
    for (const section of sections) {
        const parentId = section.metadata.parent_id;
        if (!childrenByParent.has(parentId)) {
            childrenByParent.set(parentId, []);
        }
        childrenByParent.get(parentId).push(section.header);
    }
    return childrenByParent;
}

/**
 * Siblings are the sections that share a parent_id, minus the section itself.
 *
 * @param {Object} section - A section returned by splitText
 * @param {Map<(number|null), string[]>} childrenByParent - Result of groupHeadersByParent
 * @returns {string[]} Headers of the sibling sections
 */
function siblingsOf(section, childrenByParent) {
    return childrenByParent.get(section.metadata.parent_id).filter(header => header !== section.header);
}

/**
 * Demonstrate basic usage of the MCP client.
 * 
 * Shows how to split a simple Markdown document and display
 * the resulting sections with their hierarchy information.
 * 
 * @async
 * @function exampleBasicUsage
 * @returns {Promise<void>}
 */
async function exampleBasicUsage() {
    console.log('=== Basic Usage Example ===');

    const markdownText = `
# Getting Started Guide
Welcome to our comprehensive guide.

## Prerequisites
Before you begin, ensure you have the following.

### System Requirements
Your system should meet these requirements.

### Software Dependencies
Install the required software.

## Installation Process
Follow these steps to install.

### Download
Download the latest version.

### Setup
Run the setup process.

## Configuration
Configure your installation.

### Basic Settings
Set up basic configuration.

### Advanced Settings
Configure advanced options.
`;

    const client = new MarkdownMCPClient();

    try {
        const sections = await client.splitText(markdownText);
        
        console.log(`Split document into ${sections.length} sections:\n`);

        const childrenByParent = groupHeadersByParent(sections);

        sections.forEach((section, index) => {
            console.log(`Section ${index + 1}:`);
            console.log(`  Header: ${section.header}`);
            console.log(`  Level: ${section.level}`);
            console.log(`  Parents: ${JSON.stringify(section.metadata.parents)}`);
            console.log(`  Siblings: ${JSON.stringify(siblingsOf(section, childrenByParent))}`);
            console.log(`  Content: ${section.content.substring(0, 50)}...`);
            console.log();
        });

    } catch (error) {
        console.error('Error:', error.message);
    }
}

/**
 * Demonstrate table of contents generation from Markdown.
 * 
 * Shows how to process a structured document and generate
 * a hierarchical table of contents with sibling relationships.
 * 
 * @async
 * @function exampleTableOfContents
 * @returns {Promise<void>}
 */
async function exampleTableOfContents() {
    console.log('=== Table of Contents Generator Example ===');

    const markdownText = `
# User Manual

This manual covers all aspects of using our software.

## Chapter 1: Introduction
Learn about the basics.

### What is This Software?
Overview of the software capabilities.

### Who Should Use This?
Target audience information.

## Chapter 2: Installation
Step-by-step installation guide.

### Windows Installation
Installation steps for Windows.

### macOS Installation
Installation steps for macOS.

### Linux Installation
Installation steps for Linux.

## Chapter 3: Basic Usage
Learn the fundamentals.

### Creating Your First Project
Step-by-step project creation.

### Understanding the Interface
Guide to the user interface.

## Chapter 4: Advanced Features
Explore advanced capabilities.

### Automation Tools
Learn about automation features.

### Integration Options
Connect with other tools.

## Appendix
Additional resources and information.

### Troubleshooting
Common issues and solutions.

### FAQ
Frequently asked questions.
`;

    const client = new MarkdownMCPClient();

    try {
        const sections = await client.splitText(markdownText);
        
        console.log('Generated Table of Contents:');
        console.log('-'.repeat(40));

        sections.forEach(section => {
            const indent = '  '.repeat(Math.max(section.level - 1, 0));
            const bullet = section.level === 1 ? '•' : '◦';
            console.log(`${indent}${bullet} ${section.header}`);
        });

        console.log('\nSection Navigation Map:');
        console.log('-'.repeat(40));

        const childrenByParent = groupHeadersByParent(sections);
        sections.forEach(section => {
            const siblings = siblingsOf(section, childrenByParent);
            if (siblings.length > 0) {
                console.log(`"${section.header}" → Related: ${siblings.join(', ')}`);
            }
        });

    } catch (error) {
        console.error('Error:', error.message);
    }
}

/**
 * Demonstrate content analysis and statistics generation.
 * 
 * Shows how to analyze document structure, count sections by level,
 * calculate content statistics, and visualize document hierarchy.
 * 
 * @async
 * @function exampleContentAnalysis
 * @returns {Promise<void>}
 */
async function exampleContentAnalysis() {
    console.log('=== Content Analysis Example ===');

    const markdownText = `
# Project Documentation

## Overview
This project implements a document processing system.

### Architecture
The system uses a modular architecture.

### Components
Key components include:
- Parser module
- Processor engine  
- Output formatter

## Development Guide
Instructions for developers.

### Setup Development Environment
Follow these steps to set up your environment.

### Code Structure
Understanding the codebase organization.

### Testing
How to run and write tests.

## Deployment
Production deployment information.

### Server Requirements
Hardware and software requirements.

### Configuration
Environment configuration steps.
`;

    const client = new MarkdownMCPClient();

    try {
        const sections = await client.splitText(markdownText);
        
        // Analyze content statistics
        const stats = {
            totalSections: sections.length,
            levelCounts: {},
            averageContentLength: 0,
            sectionsWithSiblings: 0
        };

        let totalContentLength = 0;
        const childrenByParent = groupHeadersByParent(sections);

        sections.forEach(section => {
            // Count by level
            const level = section.level;
            stats.levelCounts[level] = (stats.levelCounts[level] || 0) + 1;
            
            // Content length
            totalContentLength += section.content.length;
            
            // Sections with siblings
            if (siblingsOf(section, childrenByParent).length > 0) {
                stats.sectionsWithSiblings++;
            }
        });

        stats.averageContentLength = Math.round(totalContentLength / sections.length);

        console.log('Content Analysis Results:');
        console.log('-'.repeat(40));
        console.log(`Total sections: ${stats.totalSections}`);
        console.log(`Sections by level:`);
        
        Object.entries(stats.levelCounts)
            .sort(([a], [b]) => parseInt(a) - parseInt(b))
            .forEach(([level, count]) => {
                console.log(`  Level ${level}: ${count} sections`);
            });

        console.log(`Average content length: ${stats.averageContentLength} characters`);
        console.log(`Sections with siblings: ${stats.sectionsWithSiblings}`);

        console.log('\nDocument Structure Tree:');
        console.log('-'.repeat(40));
        
        sections.forEach(section => {
            const indent = '│ '.repeat(Math.max(section.level - 1, 0));
            const connector = section.level === 1 ? '├─' : '├─';
            console.log(`${indent}${connector} ${section.header}`);
        });

    } catch (error) {
        console.error('Error:', error.message);
    }
}

/**
 * Main function that runs all example demonstrations.
 * 
 * Executes the basic usage, table of contents, and content analysis
 * examples in sequence, with proper error handling and user guidance.
 * 
 * @async
 * @function main
 * @returns {Promise<void>}
 */
async function main() {
    console.log('Markdown MCP Server - JavaScript Client Examples');
    console.log('='.repeat(50));
    console.log();

    try {
        await exampleBasicUsage();
        console.log();
        
        await exampleTableOfContents();
        console.log();
        
        await exampleContentAnalysis();
        
    } catch (error) {
        console.error('Failed to run examples:', error.message);
        console.log('\nTroubleshooting:');
        console.log('1. Make sure the MCP server is running:');
        console.log('   poetry run python src/main.py');
        console.log('2. Verify server is accessible:');
        console.log('   curl http://localhost:8080/server/mcp/');
        console.log('3. Check server logs for errors');
    }
}

// Run examples if this file is executed directly
if (require.main === module) {
    main();
}