'use client'

import { useState } from 'react'
import { motion } from 'motion/react'

interface HFModel {
  id: string
  name: string
  parameters: number
  size: string
  description: string
  downloads: number
  likes: number
  tags: string[]
}

interface HuggingFaceModelLoaderProps {
  onModelSelect: (model: HFModel) => void
  isOpen: boolean
  onClose: () => void
}

// Popular models from Hugging Face
const POPULAR_MODELS: HFModel[] = [
  {
    id: 'gpt2',
    name: 'GPT-2',
    parameters: 124000000,
    size: '500 MB',
    description: 'Original GPT-2 language model',
    downloads: 5000000,
    likes: 15000,
    tags: ['text-generation', 'language-model'],
  },
  {
    id: 'distilgpt2',
    name: 'DistilGPT-2',
    parameters: 82000000,
    size: '330 MB',
    description: 'Distilled version of GPT-2',
    downloads: 3000000,
    likes: 10000,
    tags: ['text-generation', 'distilled'],
  },
  {
    id: 'gpt2-medium',
    name: 'GPT-2 Medium',
    parameters: 355000000,
    size: '1.4 GB',
    description: 'Medium-sized GPT-2 model',
    downloads: 2000000,
    likes: 8000,
    tags: ['text-generation', 'larger-model'],
  },
  {
    id: 'gpt2-large',
    name: 'GPT-2 Large',
    parameters: 774000000,
    size: '3.0 GB',
    description: 'Large GPT-2 model',
    downloads: 1500000,
    likes: 6000,
    tags: ['text-generation', 'large-model'],
  },
  {
    id: 'microsoft/DialoGPT-small',
    name: 'DialoGPT-small',
    parameters: 117000000,
    size: '470 MB',
    description: 'Small dialogue model',
    downloads: 1000000,
    likes: 5000,
    tags: ['dialogue', 'conversation'],
  },
  {
    id: 'microsoft/DialoGPT-medium',
    name: 'DialoGPT-medium',
    parameters: 345000000,
    size: '1.3 GB',
    description: 'Medium dialogue model',
    downloads: 800000,
    likes: 4000,
    tags: ['dialogue', 'conversation'],
  },
  {
    id: 'meta-llama/Llama-2-7b',
    name: 'Llama 2 (7B)',
    parameters: 7000000000,
    size: '13.5 GB',
    description: 'Meta Llama 2 7 billion parameters',
    downloads: 500000,
    likes: 3000,
    tags: ['llama', 'large-language-model'],
  },
  {
    id: 'meta-llama/Llama-2-13b',
    name: 'Llama 2 (13B)',
    parameters: 13000000000,
    size: '25 GB',
    description: 'Meta Llama 2 13 billion parameters',
    downloads: 300000,
    likes: 2000,
    tags: ['llama', 'large-language-model'],
  },
  {
    id: 'mistralai/Mistral-7B',
    name: 'Mistral 7B',
    parameters: 7000000000,
    size: '14 GB',
    description: 'Mistral 7 billion parameter model',
    downloads: 400000,
    likes: 2500,
    tags: ['mistral', 'large-language-model'],
  },
  {
    id: 'EleutherAI/gpt-j-6B',
    name: 'GPT-J (6B)',
    parameters: 6000000000,
    size: '12 GB',
    description: 'EleutherAI GPT-J 6 billion parameters',
    downloads: 600000,
    likes: 3500,
    tags: ['gpt-j', 'large-language-model'],
  },
  {
    id: 'facebook/opt-6.7b',
    name: 'OPT (6.7B)',
    parameters: 6700000000,
    size: '13 GB',
    description: 'Facebook OPT 6.7 billion parameters',
    downloads: 300000,
    likes: 1500,
    tags: ['opt', 'large-language-model'],
  },
  {
    id: 'bigscience/bloom-560m',
    name: 'BLOOM (560M)',
    parameters: 560000000,
    size: '1.1 GB',
    description: 'BigScience BLOOM 560 million parameters',
    downloads: 200000,
    likes: 1000,
    tags: ['bloom', 'multilingual'],
  },
]

export default function HuggingFaceModelLoader({ onModelSelect, isOpen, onClose }: HuggingFaceModelLoaderProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedModel, setSelectedModel] = useState<HFModel | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [filterTag, setFilterTag] = useState<string | null>(null)

  if (!isOpen) return null

  // Filter models based on search query and tag
  const filteredModels = POPULAR_MODELS.filter((model) => {
    const matchesSearch =
      model.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      model.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      model.description.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesTag = !filterTag || model.tags.includes(filterTag)

    return matchesSearch && matchesTag
  })

  // Get unique tags
  const allTags = Array.from(new Set(POPULAR_MODELS.flatMap((m) => m.tags)))

  const handleSelectModel = (model: HFModel) => {
    setSelectedModel(model)
  }

  const handleLoadModel = async () => {
    if (!selectedModel) return

    setIsLoading(true)
    try {
      // Simulate loading delay
      await new Promise((resolve) => setTimeout(resolve, 1000))
      onModelSelect(selectedModel)
      onClose()
    } catch (error) {
      console.error('Failed to load model:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden border border-white/10 shadow-2xl flex flex-col"
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 border-b border-white/10 p-6 flex-shrink-0">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-white mb-1">Load Model from Hugging Face</h2>
              <p className="text-white/60 text-sm">Search and select from popular models</p>
            </div>
            <button
              onClick={onClose}
              className="text-white/60 hover:text-white transition-colors text-2xl"
            >
              ✕
            </button>
          </div>

          {/* Search Bar */}
          <div className="relative">
            <svg className="absolute left-3 top-3 w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search models by name or description..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-white/10 bg-white/5 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
            />
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto flex-1 p-6">
          {/* Filter Tags */}
          <div className="mb-6">
            <p className="text-xs font-semibold text-white/70 mb-3">Filter by tag:</p>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setFilterTag(null)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                  filterTag === null
                    ? 'bg-emerald-500 text-white'
                    : 'bg-white/10 text-white/70 hover:bg-white/20'
                }`}
              >
                All
              </button>
              {allTags.map((tag) => (
                <button
                  key={tag}
                  onClick={() => setFilterTag(tag)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                    filterTag === tag
                      ? 'bg-emerald-500 text-white'
                      : 'bg-white/10 text-white/70 hover:bg-white/20'
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>

          {/* Models Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredModels.length > 0 ? (
              filteredModels.map((model) => (
                <motion.button
                  key={model.id}
                  onClick={() => handleSelectModel(model)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`p-4 rounded-xl border-2 transition-all text-left ${
                    selectedModel?.id === model.id
                      ? 'border-emerald-500 bg-emerald-500/10'
                      : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/10'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-white">{model.name}</h3>
                      <p className="text-xs text-white/60 mt-1">{model.id}</p>
                    </div>
                    {selectedModel?.id === model.id && (
                      <svg className="w-5 h-5 text-emerald-400 flex-shrink-0 ml-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>

                  <p className="text-sm text-white/70 mb-3">{model.description}</p>

                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-2 mb-3">
                    <div className="bg-white/5 rounded p-2">
                      <p className="text-xs text-white/60">Parameters</p>
                      <p className="text-sm font-semibold text-emerald-400">
                        {model.parameters > 1000000000
                          ? `${(model.parameters / 1000000000).toFixed(1)}B`
                          : `${(model.parameters / 1000000).toFixed(0)}M`}
                      </p>
                    </div>
                    <div className="bg-white/5 rounded p-2">
                      <p className="text-xs text-white/60">Size</p>
                      <p className="text-sm font-semibold text-cyan-400">{model.size}</p>
                    </div>
                    <div className="bg-white/5 rounded p-2">
                      <p className="text-xs text-white/60">Downloads</p>
                      <p className="text-sm font-semibold text-blue-400">
                        {model.downloads > 1000000
                          ? `${(model.downloads / 1000000).toFixed(1)}M`
                          : `${(model.downloads / 1000).toFixed(0)}K`}
                      </p>
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1">
                    {model.tags.map((tag) => (
                      <span key={tag} className="text-xs bg-white/10 text-white/70 px-2 py-1 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                </motion.button>
              ))
            ) : (
              <div className="col-span-full flex flex-col items-center justify-center py-12">
                <svg className="w-12 h-12 text-white/40 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-white/60">No models found matching your search</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-white/10 bg-white/5 p-6 flex gap-3 justify-end flex-shrink-0">
          <button
            onClick={onClose}
            className="px-6 py-2 rounded-lg border border-white/20 text-white hover:bg-white/10 transition-all"
          >
            Cancel
          </button>
          <button
            onClick={handleLoadModel}
            disabled={!selectedModel || isLoading}
            className="px-6 py-2 rounded-lg bg-emerald-500 text-white font-medium hover:bg-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <span className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Loading...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Load Model
              </>
            )}
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}
