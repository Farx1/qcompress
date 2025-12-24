'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Loader2, Zap, Sparkles, AlertCircle, MessageSquare } from 'lucide-react'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Textarea } from '@/components/ui/textarea'

export default function ChatInterface() {
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [useCompressed, setUseCompressed] = useState(false)
  const [generationTime, setGenerationTime] = useState(0)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim()) return

    setLoading(true)
    setResponse('')
    setError(null)
    setGenerationTime(0)

    const startTime = performance.now()

    try {
      const result = await apiClient.chat(prompt, {
        use_compressed: useCompressed,
        max_length: 150,
        temperature: 0.7,
      })
      const endTime = performance.now()
      setGenerationTime(endTime - startTime)
      setResponse(result.response || 'No response received')
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage = error instanceof Error ? error.message : 'Unable to generate response'
      setError(errorMessage)
      setResponse('')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full space-y-6">
      <AnimatePresence>
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Card className="border-destructive/50 bg-destructive/10">
              <CardContent className="pt-6">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-destructive" />
                  <p className="text-destructive text-sm font-medium">Error: {error}</p>
                </div>
              </CardContent>
            </Card>
        </motion.div>
      )}
      </AnimatePresence>

      {/* Model Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Model Selection</CardTitle>
          <CardDescription>Choose between original or compressed model</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
          <label className="flex items-center cursor-pointer group">
            <div className="relative">
              <input
                type="checkbox"
                checked={useCompressed}
                onChange={(e) => setUseCompressed(e.target.checked)}
                className="sr-only"
              />
                  <div
                    className={`w-6 h-6 rounded-md border-2 transition-all duration-300 flex items-center justify-center ${
                useCompressed
                        ? 'border-quantum-emerald-500 bg-quantum-emerald-500/20'
                        : 'border-border bg-muted group-hover:border-quantum-emerald-500/50'
                    }`}
                  >
                {useCompressed && (
                      <svg
                        className="w-4 h-4 text-quantum-emerald-400"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                  </svg>
                )}
              </div>
            </div>
                <span className="text-sm font-medium ml-3">
                  {useCompressed ? 'Compressed Model' : 'Original Model'}
            </span>
          </label>
            </div>
            <Badge variant={useCompressed ? 'default' : 'secondary'}>
              {useCompressed ? (
                <>
                  <Zap className="h-3 w-3 mr-1" />
                  Fast & Light
                </>
              ) : (
                <>
                  <Sparkles className="h-3 w-3 mr-1" />
                  High Quality
                </>
              )}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Your Prompt</CardTitle>
            <CardDescription>Enter your prompt to generate a response</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="prompt">Prompt</Label>
              <Textarea
                id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={6}
                placeholder="Enter your prompt here... For example: 'Explain Tensor-Train compression in one sentence'"
                className="resize-none"
          />
              <div className="text-xs text-muted-foreground">
                {prompt.length} characters
          </div>
        </div>
          </CardContent>
        </Card>

        <Button
          type="submit"
          disabled={loading || !prompt.trim()}
          className="w-full"
          size="lg"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Send className="h-4 w-4 mr-2" />
              Generate Response
            </>
          )}
        </Button>
      </form>

      {/* Response Display */}
      <AnimatePresence>
      {response && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Generated Response</CardTitle>
            {generationTime > 0 && (
                    <Badge variant="secondary" className="gap-1">
                      <Zap className="h-3 w-3" />
                      {generationTime.toFixed(0)}ms
                    </Badge>
            )}
          </div>
              </CardHeader>
              <CardContent>
                <div className="bg-muted rounded-lg p-4 border border-border">
                  <p className="whitespace-pre-wrap leading-relaxed text-sm">
              {response}
            </p>
          </div>
              </CardContent>
            </Card>
        </motion.div>
      )}
      </AnimatePresence>

      {/* Loading State */}
      <AnimatePresence>
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col items-center justify-center gap-4 py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                  <p className="text-muted-foreground text-sm">Generating response...</p>
          </div>
              </CardContent>
            </Card>
        </motion.div>
      )}
      </AnimatePresence>

      {/* Empty State */}
      {!response && !loading && !error && (
        <Card className="border-dashed">
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center gap-4 py-12">
              <MessageSquare className="h-12 w-12 text-muted-foreground/30" />
              <div className="text-center">
                <p className="text-sm font-medium mb-1">No response yet</p>
                <p className="text-xs text-muted-foreground">
                  Enter a prompt and click "Generate Response"
                </p>
              </div>
        </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
