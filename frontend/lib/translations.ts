export type Language = 'en' | 'fr';

export const translations = {
  en: {
    // Navigation
    'nav.features': 'Features',
    'nav.howItWorks': 'How it works',
    'nav.dashboard': 'Dashboard',
    'nav.language': 'Language',

    // Home page - Hero
    'home.badge': 'New compression technology',
    'home.title': 'Compress your LLMs',
    'home.titleHighlight': 'without losing performance',
    'home.description': 'QCompress uses Tensor-Train decomposition to reduce your model size up to 10x. Maintain quality while drastically reducing resources required for inference.',
    'home.ctaStart': 'Get started now',
    'home.ctaLearn': 'Learn more',

    // Home page - Stats
    'home.stat1Label': 'Size reduction',
    'home.stat1Value': 'up to 10x',
    'home.stat2Label': 'Performance maintained',
    'home.stat2Value': '>95%',
    'home.stat3Label': 'Inference time',
    'home.stat3Value': '-70%',

    // Home page - Features
    'home.featuresTitle': 'Main Features',
    'home.featuresSubtitle': 'Everything you need to compress and optimize your models',
    'home.feature1Title': 'Fast Compression',
    'home.feature1Desc': 'Reduce your LLM model size up to 10x without losing efficiency.',
    'home.feature2Title': 'TT Decomposition',
    'home.feature2Desc': 'Quantum-inspired technology that factors weight matrices into tensors.',
    'home.feature3Title': 'Real-time Monitoring',
    'home.feature3Desc': 'Visualize metrics live via WebSocket. Track every step.',
    'home.feature4Title': 'Performance Maintained',
    'home.feature4Desc': 'Keep your models\' quality while reducing resources.',

    // Home page - How it works
    'home.howItWorksTitle': 'How it works',
    'home.howItWorksSubtitle': 'Four simple steps to compress your model',
    'home.step1Title': 'Select',
    'home.step1Desc': 'Choose a model (GPT-2, DistilGPT-2, DialoGPT)',
    'home.step2Title': 'Configure',
    'home.step2Desc': 'Set TT parameters: modes, ranks and penalties',
    'home.step3Title': 'Launch',
    'home.step3Desc': 'Start and monitor metrics in real-time',
    'home.step4Title': 'Test',
    'home.step4Desc': 'Compare models in the chat arena',

    // Home page - CTA
    'home.ctaTitle': 'Ready to get started?',
    'home.ctaDesc': 'Access the dashboard to configure and launch your first compression now',

    // Dashboard
    'dashboard.title': 'Compression Dashboard',
    'dashboard.subtitle': 'Professional interface for compression and model monitoring.',
    'dashboard.newCompression': 'New compression',
    'dashboard.menu': 'Menu',

    // Dashboard tabs
    'dashboard.tabOverview': 'Overview',
    'dashboard.tabMonitoring': 'Monitoring',
    'dashboard.tabBenchmarks': 'Benchmarks',
    'dashboard.tabCores': 'TT Cores',
    'dashboard.tabChat': 'Chat Arena',

    // Dashboard - Overview
    'dashboard.availableModels': 'Available Models',
    'dashboard.compressionMetrics': 'Compression Metrics',
    'dashboard.totalJobs': 'Total Jobs',
    'dashboard.completed': 'Completed',
    'dashboard.avgCompression': 'Avg Compression',

    // Dashboard - Monitoring
    'dashboard.selectModel': 'Select a model',
    'dashboard.startCompression': 'Start compression',
    'dashboard.monitoring': 'Monitoring',
    'dashboard.visualization': 'Visualization',
    'dashboard.benchmark': 'Benchmark',
    'dashboard.noMetrics': 'No metrics data available',

    // Dashboard - Chat
    'dashboard.chatArena': 'Chat Arena',
    'dashboard.compareModels': 'Compare model generations.',
    'dashboard.selectChatModel': 'Select a model',
    'dashboard.enterPrompt': 'Enter your prompt here...',
    'dashboard.generate': 'Generate',
    'dashboard.generating': 'Generating...',

    // Compression Wizard
    'wizard.title': 'New Compression',
    'wizard.selectModel': 'Select Model',
    'wizard.selectModelDesc': 'Choose a model to compress',
    'wizard.loadModel': 'Load from Hugging Face',
    'wizard.modelName': 'Model name (e.g., gpt2, distilgpt2)',
    'wizard.configure': 'Configure Parameters',
    'wizard.configureDesc': 'Set compression parameters',
    'wizard.compressionRatio': 'Compression Ratio',
    'wizard.targetRank': 'Target Rank',
    'wizard.penaltyWeight': 'Penalty Weight',
    'wizard.review': 'Review & Launch',
    'wizard.reviewDesc': 'Review your compression settings',
    'wizard.launch': 'Launch Compression',
    'wizard.launching': 'Launching...',
    'wizard.cancel': 'Cancel',
    'wizard.next': 'Next',
    'wizard.back': 'Back',
    'wizard.success': 'Compression started successfully!',
    'wizard.error': 'Error starting compression',

    // Model Loader
    'models.loadFromHF': 'Load from Hugging Face',
    'models.search': 'Search models...',
    'models.loading': 'Loading models...',
    'models.error': 'Error loading models',
    'models.noResults': 'No models found',
    'models.parameters': 'parameters',
    'models.size': 'size',

    // Common
    'common.loading': 'Loading...',
    'common.error': 'Error',
    'common.success': 'Success',
    'common.cancel': 'Cancel',
    'common.save': 'Save',
    'common.delete': 'Delete',
    'common.edit': 'Edit',
    'common.close': 'Close',
    'common.status': 'Status',
    'common.progress': 'Progress',
  },
  fr: {
    // Navigation
    'nav.features': 'Fonctionnalités',
    'nav.howItWorks': 'Comment ça marche',
    'nav.dashboard': 'Dashboard',
    'nav.language': 'Langue',

    // Home page - Hero
    'home.badge': 'Nouvelle technologie de compression',
    'home.title': 'Compressez vos LLMs',
    'home.titleHighlight': 'sans perdre en performance',
    'home.description': 'QCompress utilise la décomposition Tensor-Train pour réduire la taille de vos modèles jusqu\'à 10x. Maintenez la qualité tout en réduisant drastiquement les ressources requises pour l\'inférence.',
    'home.ctaStart': 'Commencer maintenant',
    'home.ctaLearn': 'En savoir plus',

    // Home page - Stats
    'home.stat1Label': 'Réduction de taille',
    'home.stat1Value': 'jusqu\'à 10x',
    'home.stat2Label': 'Performance maintenue',
    'home.stat2Value': '>95%',
    'home.stat3Label': 'Temps d\'inférence',
    'home.stat3Value': '-70%',

    // Home page - Features
    'home.featuresTitle': 'Fonctionnalités Principales',
    'home.featuresSubtitle': 'Tout ce dont vous avez besoin pour compresser et optimiser vos modèles',
    'home.feature1Title': 'Compression Rapide',
    'home.feature1Desc': 'Réduisez la taille de vos modèles LLM jusqu\'à 10x sans perdre en efficacité.',
    'home.feature2Title': 'Décomposition TT',
    'home.feature2Desc': 'Technologie quantique-inspirée qui factorise les matrices de poids en tenseurs.',
    'home.feature3Title': 'Monitoring Temps Réel',
    'home.feature3Desc': 'Visualisez les métriques en direct via WebSocket. Suivez chaque étape.',
    'home.feature4Title': 'Performance Maintenue',
    'home.feature4Desc': 'Conservez la qualité de vos modèles tout en réduisant les ressources.',

    // Home page - How it works
    'home.howItWorksTitle': 'Comment ça marche',
    'home.howItWorksSubtitle': 'Quatre étapes simples pour compresser votre modèle',
    'home.step1Title': 'Sélectionner',
    'home.step1Desc': 'Choisissez un modèle (GPT-2, DistilGPT-2, DialoGPT)',
    'home.step2Title': 'Configurer',
    'home.step2Desc': 'Définissez les paramètres TT : modes, rangs et pénalités',
    'home.step3Title': 'Lancer',
    'home.step3Desc': 'Démarrez et surveillez les métriques en temps réel',
    'home.step4Title': 'Tester',
    'home.step4Desc': 'Comparez les modèles dans l\'arène de chat',

    // Home page - CTA
    'home.ctaTitle': 'Prêt à commencer ?',
    'home.ctaDesc': 'Accédez au dashboard pour configurer et lancer votre première compression dès maintenant',

    // Dashboard
    'dashboard.title': 'Dashboard de Compression',
    'dashboard.subtitle': 'Interface professionnelle pour la compression et le monitoring de vos modèles.',
    'dashboard.newCompression': 'Nouvelle compression',
    'dashboard.menu': 'Menu',

    // Dashboard tabs
    'dashboard.tabOverview': 'Vue d\'ensemble',
    'dashboard.tabMonitoring': 'Monitoring',
    'dashboard.tabBenchmarks': 'Benchmarks',
    'dashboard.tabCores': 'Cores TT',
    'dashboard.tabChat': 'Arène Chat',

    // Dashboard - Overview
    'dashboard.availableModels': 'Modèles Disponibles',
    'dashboard.compressionMetrics': 'Métriques de Compression',
    'dashboard.totalJobs': 'Total de Jobs',
    'dashboard.completed': 'Complétés',
    'dashboard.avgCompression': 'Compression Moyenne',

    // Dashboard - Monitoring
    'dashboard.selectModel': 'Sélectionner un modèle',
    'dashboard.startCompression': 'Démarrer la compression',
    'dashboard.monitoring': 'Monitoring',
    'dashboard.visualization': 'Visualisation',
    'dashboard.benchmark': 'Benchmark',
    'dashboard.noMetrics': 'Aucune donnée de métriques disponible',

    // Dashboard - Chat
    'dashboard.chatArena': 'Arène de Chat',
    'dashboard.compareModels': 'Comparez les générations entre les modèles.',
    'dashboard.selectChatModel': 'Sélectionner un modèle',
    'dashboard.enterPrompt': 'Entrez votre prompt ici...',
    'dashboard.generate': 'Générer',
    'dashboard.generating': 'Génération en cours...',

    // Compression Wizard
    'wizard.title': 'Nouvelle Compression',
    'wizard.selectModel': 'Sélectionner un Modèle',
    'wizard.selectModelDesc': 'Choisissez un modèle à compresser',
    'wizard.loadModel': 'Charger depuis Hugging Face',
    'wizard.modelName': 'Nom du modèle (ex: gpt2, distilgpt2)',
    'wizard.configure': 'Configurer les Paramètres',
    'wizard.configureDesc': 'Définissez les paramètres de compression',
    'wizard.compressionRatio': 'Ratio de Compression',
    'wizard.targetRank': 'Rang Cible',
    'wizard.penaltyWeight': 'Poids de Pénalité',
    'wizard.review': 'Vérifier et Lancer',
    'wizard.reviewDesc': 'Vérifiez vos paramètres de compression',
    'wizard.launch': 'Lancer la Compression',
    'wizard.launching': 'Lancement en cours...',
    'wizard.cancel': 'Annuler',
    'wizard.next': 'Suivant',
    'wizard.back': 'Retour',
    'wizard.success': 'Compression lancée avec succès !',
    'wizard.error': 'Erreur au lancement de la compression',

    // Model Loader
    'models.loadFromHF': 'Charger depuis Hugging Face',
    'models.search': 'Rechercher des modèles...',
    'models.loading': 'Chargement des modèles...',
    'models.error': 'Erreur lors du chargement des modèles',
    'models.noResults': 'Aucun modèle trouvé',
    'models.parameters': 'paramètres',
    'models.size': 'taille',

    // Common
    'common.loading': 'Chargement...',
    'common.error': 'Erreur',
    'common.success': 'Succès',
    'common.cancel': 'Annuler',
    'common.save': 'Enregistrer',
    'common.delete': 'Supprimer',
    'common.edit': 'Modifier',
    'common.close': 'Fermer',
    'common.status': 'Statut',
    'common.progress': 'Progression',
  },
};

export function t(key: string, language: Language): string {
  const keys = key.split('.');
  let value: any = translations[language];
  
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k];
    } else {
      return key; // Return key if translation not found
    }
  }
  
  return typeof value === 'string' ? value : key;
}
