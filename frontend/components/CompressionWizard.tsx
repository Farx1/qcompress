'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, ChevronRight, Loader2, Sparkles, Settings, Eye, X } from 'lucide-react'
import { toast } from 'sonner'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Slider } from '@/components/ui/slider'
import { Separator } from '@/components/ui/separator'
import HuggingFaceModelLoader from './HuggingFaceModelLoader'

interface Model {
  id: string
  name: string
  parameters: number
  size: string
  description: string
}

interface CompressionConfig {
  modelId: string
  modelName: string
  compressionRatio: number
  targetRank: number
  penaltyWeight: number
}

interface CompressionWizardProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (config: CompressionConfig) => void
  isLoading?: boolean
}

const steps = [
  { id: 1, title: 'Select Model', icon: Sparkles },
  { id: 2, title: 'Configure', icon: Settings },
  { id: 3, title: 'Review', icon: Eye },
]

export default function CompressionWizard({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
}: CompressionWizardProps) {
  const [step, setStep] = useState(1)
  const [showModelLoader, setShowModelLoader] = useState(false)
  const [selectedModel, setSelectedModel] = useState<Model | null>(null)
  const [compressionRatio, setCompressionRatio] = useState([0.5])
  const [targetRank, setTargetRank] = useState([10])
  const [penaltyWeight, setPenaltyWeight] = useState([0.1])

  const defaultModels: Model[] = [
    {
      id: 'distilgpt2',
      name: 'DistilGPT-2',
      parameters: 82000000,
      size: '330 MB',
      description: 'Lightweight model based on GPT-2',
    },
    {
      id: 'gpt2',
      name: 'GPT-2',
      parameters: 124000000,
      size: '500 MB',
      description: 'Original GPT-2 language model',
    },
    {
      id: 'microsoft/DialoGPT-small',
      name: 'DialoGPT-small',
      parameters: 117000000,
      size: '470 MB',
      description: 'Dialogue model based on GPT-2',
    },
  ]

  const handleSelectModel = (model: Model) => {
    setSelectedModel(model)
    setStep(2)
  }

  const handleSubmit = () => {
    if (!selectedModel) return

    onSubmit({
      modelId: selectedModel.id,
      modelName: selectedModel.name,
      compressionRatio: compressionRatio[0],
      targetRank: targetRank[0],
      penaltyWeight: penaltyWeight[0],
    })

    // Reset wizard
    setStep(1)
    setSelectedModel(null)
    setCompressionRatio([0.5])
    setTargetRank([10])
    setPenaltyWeight([0.1])
  }

  const handleClose = () => {
    setStep(1)
    setSelectedModel(null)
    setCompressionRatio([0.5])
    setTargetRank([10])
    setPenaltyWeight([0.1])
    onClose()
  }

  const progressPercentage = (step / steps.length) * 100

  return (
    <>
      <Dialog open={isOpen} onOpenChange={handleClose}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>New Compression Job</DialogTitle>
            <DialogDescription>
              Configure and launch a new model compression
            </DialogDescription>
          </DialogHeader>

          {/* Progress Steps */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              {steps.map((s, index) => {
                const Icon = s.icon
                const isActive = step === s.id
                const isCompleted = step > s.id

                return (
                  <div key={s.id} className="flex items-center flex-1">
                    <div className="flex flex-col items-center flex-1">
    <motion.div
                        className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${
                          isActive
                            ? 'border-primary bg-primary/20 text-primary'
                            : isCompleted
                            ? 'border-quantum-emerald-500 bg-quantum-emerald-500/20 text-quantum-emerald-300'
                            : 'border-muted bg-muted text-muted-foreground'
                        }`}
                        animate={isActive ? { scale: [1, 1.1, 1] } : {}}
                        transition={{ duration: 0.3 }}
                      >
                        {isCompleted ? (
                          <Check className="h-5 w-5" />
                        ) : (
                          <Icon className="h-5 w-5" />
                        )}
                      </motion.div>
                      <span
                        className={`mt-2 text-xs font-medium ${
                          isActive ? 'text-foreground' : 'text-muted-foreground'
                        }`}
                      >
                        {s.title}
                      </span>
                    </div>
                    {index < steps.length - 1 && (
                      <div className="flex-1 h-0.5 mx-2 bg-muted">
      <motion.div
                          className="h-full bg-gradient-to-r from-primary to-quantum-cyan-500"
                          initial={{ width: 0 }}
                          animate={{ width: step > s.id ? '100%' : '0%' }}
                          transition={{ duration: 0.3 }}
                        />
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
            <Progress value={progressPercentage} />
        </div>

        {/* Content */}
        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
                className="space-y-4"
            >
              <div>
                  <h3 className="text-lg font-semibold mb-2">Select Model</h3>
                  <p className="text-sm text-muted-foreground">Choose a model to compress</p>
              </div>

              <div className="space-y-3">
                  {defaultModels.map((model, index) => (
                    <motion.div
                    key={model.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Card
                        className="cursor-pointer hover:border-primary transition-colors"
                    onClick={() => handleSelectModel(model)}
                  >
                        <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <CardTitle className="text-base">{model.name}</CardTitle>
                                <Badge variant="secondary">Default</Badge>
                              </div>
                              <CardDescription>{model.description}</CardDescription>
                              <div className="flex gap-4 mt-3 text-xs text-muted-foreground">
                          <span>{(model.parameters / 1000000).toFixed(0)}M parameters</span>
                          <span>{model.size}</span>
                        </div>
                      </div>
                            <ChevronRight className="h-5 w-5 text-muted-foreground flex-shrink-0 mt-1" />
                    </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                ))}
              </div>

                <Button
                  variant="outline"
                  className="w-full"
                onClick={() => setShowModelLoader(true)}
              >
                  <Sparkles className="h-4 w-4 mr-2" />
                Load from Hugging Face
                </Button>
            </motion.div>
          )}

          {step === 2 && selectedModel && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              <div>
                  <h3 className="text-lg font-semibold mb-2">Configure Parameters</h3>
                  <p className="text-sm text-muted-foreground">Set compression parameters</p>
              </div>

                <Card className="border-quantum-emerald-500/30 bg-quantum-emerald-500/10">
                  <CardContent className="pt-6">
                    <p className="text-sm text-muted-foreground mb-1">Selected Model</p>
                    <p className="font-semibold">{selectedModel.name}</p>
                  </CardContent>
                </Card>

              {/* Compression Ratio */}
                <div className="space-y-2">
                  <Label>
                    Compression Ratio: <span className="text-primary">{Math.round(compressionRatio[0] * 100)}%</span>
                  </Label>
                  <Slider
                  value={compressionRatio}
                    onValueChange={setCompressionRatio}
                    min={0.1}
                    max={0.9}
                    step={0.1}
                />
                  <div className="flex justify-between text-xs text-muted-foreground">
                  <span>10%</span>
                  <span>90%</span>
                </div>
              </div>

              {/* Target Rank */}
                <div className="space-y-2">
                  <Label>
                    Target Rank: <span className="text-primary">{targetRank[0]}</span>
                  </Label>
                  <Slider
                  value={targetRank}
                    onValueChange={setTargetRank}
                    min={1}
                    max={50}
                    step={1}
                />
                  <div className="flex justify-between text-xs text-muted-foreground">
                  <span>1</span>
                  <span>50</span>
                </div>
              </div>

              {/* Penalty Weight */}
                <div className="space-y-2">
                  <Label>
                    Penalty Weight: <span className="text-primary">{penaltyWeight[0].toFixed(2)}</span>
                  </Label>
                  <Slider
                  value={penaltyWeight}
                    onValueChange={setPenaltyWeight}
                    min={0.01}
                    max={1}
                    step={0.01}
                />
                  <div className="flex justify-between text-xs text-muted-foreground">
                  <span>0.01</span>
                  <span>1.00</span>
                </div>
              </div>
            </motion.div>
          )}

          {step === 3 && selectedModel && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              <div>
                  <h3 className="text-lg font-semibold mb-2">Review & Launch</h3>
                  <p className="text-sm text-muted-foreground">Review your compression settings</p>
                </div>

                <div className="space-y-4">
                  <Card>
                    <CardContent className="pt-6">
                      <p className="text-sm text-muted-foreground mb-1">Model</p>
                      <p className="font-semibold">{selectedModel.name}</p>
                    </CardContent>
                  </Card>

                <div className="grid grid-cols-3 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <p className="text-sm text-muted-foreground mb-1">Compression Ratio</p>
                        <p className="font-semibold">{Math.round(compressionRatio[0] * 100)}%</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <p className="text-sm text-muted-foreground mb-1">Target Rank</p>
                        <p className="font-semibold">{targetRank[0]}</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <p className="text-sm text-muted-foreground mb-1">Penalty Weight</p>
                        <p className="font-semibold">{penaltyWeight[0].toFixed(2)}</p>
                      </CardContent>
                    </Card>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

          <Separator />

        {/* Buttons */}
          <div className="flex gap-4">
            <Button variant="outline" onClick={handleClose} disabled={isLoading} className="flex-1">
            Cancel
            </Button>

          {step > 1 && (
              <Button
                variant="outline"
              onClick={() => setStep(step - 1)}
              disabled={isLoading}
                className="flex-1"
            >
              Back
              </Button>
          )}

          {step < 3 ? (
              <Button
              onClick={() => setStep(step + 1)}
              disabled={isLoading || (step === 1 && !selectedModel)}
                className="flex-1"
            >
              Next
              </Button>
          ) : (
              <Button onClick={handleSubmit} disabled={isLoading} className="flex-1">
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Launching...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Launch Compression
                  </>
                )}
              </Button>
          )}
        </div>
        </DialogContent>
      </Dialog>

      {/* Model Loader Modal */}
      <HuggingFaceModelLoader
        isOpen={showModelLoader}
        onClose={() => setShowModelLoader(false)}
        onModelSelect={handleSelectModel}
      />
    </>
  )
}
