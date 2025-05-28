import type { Request, Response } from "express"
import express from "express"
import { parseAndValidateConfig } from "../shared/config.js"
import type { z } from "zod"

import type { Server } from "@modelcontextprotocol/sdk/server/index.js"
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js"

/**
 * Arguments when we create a new instance of your server
 */
export interface CreateServerArg<T = Record<string, unknown>> {
	config: T
}

export type CreateServerFn<T = Record<string, unknown>> = (
	arg: CreateServerArg<T>,
) => Server

export interface CreateStatelessServerOptions<T> {
	schema?: z.ZodSchema<T>
}

/**
 * Creates a stateless server for handling MCP requests
 * In stateless mode, each request creates a new server and transport instance
 * @param createMcpServer Function to create an MCP server
 * @param options Optional configuration including Zod schema for validation
 * @returns Express app
 */
export function createStatelessServer<T = Record<string, unknown>>(
	createMcpServer: CreateServerFn<T>,
	options?: CreateStatelessServerOptions<T>,
) {
	const app = express()
	app.use(express.json())

	app.post("/mcp", async (req: Request, res: Response) => {
		// In stateless mode, create a new instance of transport and server for each request
		// to ensure complete isolation. A single instance would cause request ID collisions
		// when multiple clients connect concurrently.

		try {
			// Parse and validate config
			const configResult = parseAndValidateConfig(req, options?.schema)
			if (!configResult.ok) {
				const status = configResult.error.status
				res.status(status).json(configResult.error)
				return
			}

			const config = configResult.value

			// Create a new server instance with config
			const server = createMcpServer({ config: config as T })

			// Create a new transport instance
			const transport = new StreamableHTTPServerTransport({
				sessionIdGenerator: undefined,
			})

			// Clean up resources when the request ends
			res.on("close", () => {
				transport.close()
				server.close()
			})

			// Connect the server to the transport
			await server.connect(transport)

			// Handle the incoming request
			await transport.handleRequest(req, res, req.body)
		} catch (error) {
			console.error("Error handling MCP request:", error)
			if (!res.headersSent) {
				res.status(500).json({
					jsonrpc: "2.0",
					error: {
						code: -32603,
						message: "Internal server error",
					},
					id: null,
				})
			}
		}
	})

	app.get("/mcp", async (req: Request, res: Response) => {
		console.log("Received GET MCP request")
		res.writeHead(405).end(
			JSON.stringify({
				jsonrpc: "2.0",
				error: {
					code: -32000,
					message: "Method not allowed in stateless mode",
				},
				id: null,
			}),
		)
	})

	app.delete("/mcp", async (req: Request, res: Response) => {
		console.log("Received DELETE MCP request")
		res.writeHead(405).end(
			JSON.stringify({
				jsonrpc: "2.0",
				error: {
					code: -32000,
					message: "Method not allowed in stateless mode",
				},
				id: null,
			}),
		)
	})

	return { app }
}
