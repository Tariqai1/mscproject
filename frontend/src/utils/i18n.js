/**
 * Internationalization (i18n) Configuration
 * Supports Hindi, Spanish, and French languages
 */

const translations = {
  en: {
    common: {
      appName: 'Sarcasm Sentiment Analyzer',
      tagline: 'AI-Powered Review Analysis',
      home: 'Home',
      history: 'History',
      analytics: 'Analytics',
      timeline: 'Timeline',
      batch: 'Batch',
      compare: 'Compare',
      darkMode: 'Dark',
      lightMode: 'Light',
      login: 'Login',
      register: 'Register',
      logout: 'Logout',
      username: 'Username',
      password: 'Password',
      email: 'Email'
    },
    home: {
      title: 'Welcome to Sarcasm-Aware Sentiment Analysis',
      description: 'Analyze sentiment and detect sarcasm in text with AI',
      enterText: 'Enter a review or comment...',
      getPrediction: 'Get Prediction',
      charactersLeft: 'characters',
      features: 'Features',
      feature1: 'Sentiment Detection',
      feature2: 'Sarcasm Detection',
      feature3: 'Emotion Analysis',
      feature4: 'Real-time Feedback'
    },
    results: {
      sentiment: 'Sentiment',
      sarcasm: 'Sarcasm Detection',
      emotions: 'Detected Emotions',
      confidence: 'confidence',
      interpretation: 'Interpretation',
      explanation: 'Explanation',
      modelUsed: 'Model Used',
      wasCorrect: 'Was this analysis correct?',
      correct: 'Correct',
      incorrect: 'Incorrect'
    },
    analytics: {
      title: 'Analytics',
      totalPredictions: 'Total Predictions',
      sentimentDistribution: 'Sentiment Distribution',
      sarcasmPercentage: 'Sarcasm %',
      refresh: 'Refresh',
      exportCSV: 'Export CSV',
      exportJSON: 'Export JSON',
      exportPDF: 'Export PDF'
    },
    timeline: {
      title: 'Time-Series Analytics',
      trackTrends: 'Track sentiment and sarcasm trends over time',
      period: 'Time Period',
      lookback: 'Lookback Days',
      daily: 'Daily',
      weekly: 'Weekly',
      monthly: 'Monthly',
      predictionVolume: 'Prediction Volume Over Time',
      sentimentDistribution: 'Sentiment Distribution Over Time',
      sarcasmTrend: 'Sarcasm Detection Trend',
      confidenceTrend: 'Average Sentiment Confidence Over Time',
      statistics: 'Detailed Statistics by Period'
    },
    auth: {
      loginTitle: 'Login',
      registerTitle: 'Register',
      fullName: 'Full Name',
      confirmPassword: 'Confirm Password',
      signIn: 'Sign In',
      signUp: 'Sign Up',
      loggingIn: 'Logging in...',
      registering: 'Registering...',
      noAccount: 'Don\'t have an account?',
      haveAccount: 'Already have an account?',
      registerHere: 'Register here',
      loginHere: 'Login here',
      registrationSuccess: 'Registration successful! Redirecting to login...'
    },
    errors: {
      invalidCredentials: 'Invalid username or password',
      userExists: 'Username or email already exists',
      passwordMismatch: 'Passwords do not match',
      passwordTooShort: 'Password must be at least 6 characters',
      usernameTooShort: 'Username must be at least 3 characters'
    }
  },
  hi: {
    common: {
      appName: 'व्यंग्य भावना विश्लेषक',
      tagline: 'एआई-संचालित समीक्षा विश्लेषण',
      home: 'होम',
      history: 'इतिहास',
      analytics: 'विश्लेषण',
      timeline: 'समयरेखा',
      batch: 'बैच',
      compare: 'तुलना करें',
      darkMode: 'गहरा',
      lightMode: 'हल्का',
      login: 'लॉगिन',
      register: 'पंजीकरण',
      logout: 'लॉगआउट',
      username: 'उपयोगकर्ता नाम',
      password: 'पासवर्ड',
      email: 'ईमेल'
    },
    home: {
      title: 'व्यंग्य-जागरूक भावना विश्लेषण में स्वागत है',
      description: 'एआई के साथ पाठ में भावना का विश्लेषण करें और व्यंग्य का पता लगाएं',
      enterText: 'समीक्षा या टिप्पणी दर्ज करें...',
      getPrediction: 'भविष्यवाणी प्राप्त करें',
      charactersLeft: 'वर्ण',
      features: 'विशेषताएं',
      feature1: 'भावना का पता लगाना',
      feature2: 'व्यंग्य का पता लगाना',
      feature3: 'भावना विश्लेषण',
      feature4: 'रीयल-टाइम प्रतिक्रिया'
    },
    results: {
      sentiment: 'भावना',
      sarcasm: 'व्यंग्य का पता लगाना',
      emotions: 'पहचानी गई भावनाएं',
      confidence: 'आत्मविश्वास',
      interpretation: 'व्याख्या',
      explanation: 'व्याख्या',
      modelUsed: 'उपयोग किया गया मॉडल',
      wasCorrect: 'क्या यह विश्लेषण सही था?',
      correct: 'सही',
      incorrect: 'गलत'
    },
    analytics: {
      title: 'विश्लेषण',
      totalPredictions: 'कुल भविष्यवाणियां',
      sentimentDistribution: 'भावना वितरण',
      sarcasmPercentage: 'व्यंग्य %',
      refresh: 'ताज़ा करें',
      exportCSV: 'CSV निर्यात करें',
      exportJSON: 'JSON निर्यात करें',
      exportPDF: 'PDF निर्यात करें'
    },
    timeline: {
      title: 'समय-श्रृंखला विश्लेषण',
      trackTrends: 'समय के साथ भावना और व्यंग्य प्रवृत्तियों को ट्रैक करें',
      period: 'समय अवधि',
      lookback: 'पिछले दिन',
      daily: 'दैनिक',
      weekly: 'साप्ताहिक',
      monthly: 'मासिक',
      predictionVolume: 'समय के साथ भविष्यवाणी मात्रा',
      sentimentDistribution: 'समय के साथ भावना वितरण',
      sarcasmTrend: 'व्यंग्य पहचान प्रवृत्ति',
      confidenceTrend: 'औसत भावना आत्मविश्वास समय के साथ',
      statistics: 'अवधि द्वारा विस्तृत आंकड़े'
    },
    auth: {
      loginTitle: 'लॉगिन',
      registerTitle: 'पंजीकरण',
      fullName: 'पूरा नाम',
      confirmPassword: 'पासवर्ड की पुष्टि करें',
      signIn: 'साइन इन करें',
      signUp: 'साइन अप करें',
      loggingIn: 'लॉगिंग इन...',
      registering: 'पंजीकरण...',
      noAccount: 'खाता नहीं है?',
      haveAccount: 'पहले से खाता है?',
      registerHere: 'यहाँ पंजीकरण करें',
      loginHere: 'यहाँ लॉगिन करें',
      registrationSuccess: 'पंजीकरण सफल! लॉगिन को पुनः निर्देशित किया जा रहा है...'
    },
    errors: {
      invalidCredentials: 'अमान्य उपयोगकर्ता नाम या पासवर्ड',
      userExists: 'उपयोगकर्ता नाम या ईमेल पहले से मौजूद है',
      passwordMismatch: 'पासवर्ड मेल नहीं खाते',
      passwordTooShort: 'पासवर्ड कम से कम 6 वर्ण होना चाहिए',
      usernameTooShort: 'उपयोगकर्ता नाम कम से कम 3 वर्ण होना चाहिए'
    }
  },
  es: {
    common: {
      appName: 'Analizador de Sentimientos con Sarcasmo',
      tagline: 'Análisis de Reseñas Impulsado por IA',
      home: 'Inicio',
      history: 'Historial',
      analytics: 'Análisis',
      timeline: 'Cronología',
      batch: 'Lote',
      compare: 'Comparar',
      darkMode: 'Oscuro',
      lightMode: 'Claro',
      login: 'Iniciar Sesión',
      register: 'Registrarse',
      logout: 'Cerrar Sesión',
      username: 'Nombre de Usuario',
      password: 'Contraseña',
      email: 'Correo Electrónico'
    },
    home: {
      title: 'Bienvenido al Análisis de Sentimientos con Sarcasmo',
      description: 'Analiza sentimientos y detecta sarcasmo en textos con IA',
      enterText: 'Ingresa una reseña o comentario...',
      getPrediction: 'Obtener Predicción',
      charactersLeft: 'caracteres',
      features: 'Características',
      feature1: 'Detección de Sentimientos',
      feature2: 'Detección de Sarcasmo',
      feature3: 'Análisis de Emociones',
      feature4: 'Retroalimentación en Tiempo Real'
    },
    results: {
      sentiment: 'Sentimiento',
      sarcasm: 'Detección de Sarcasmo',
      emotions: 'Emociones Detectadas',
      confidence: 'confianza',
      interpretation: 'Interpretación',
      explanation: 'Explicación',
      modelUsed: 'Modelo Utilizado',
      wasCorrect: '¿Fue correcto este análisis?',
      correct: 'Correcto',
      incorrect: 'Incorrecto'
    }
  }
};

export const getTranslation = (language, section, key) => {
  const lang = translations[language] || translations['en'];
  return lang[section]?.[key] || translations['en'][section]?.[key] || key;
};

export const getLanguageList = () => {
  return [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'hi', name: 'हिंदी', flag: '🇮🇳' },
    { code: 'es', name: 'Español', flag: '🇪🇸' }
  ];
};

export default translations;
