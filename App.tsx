
import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { ImageUploader } from './components/ImageUploader';
import { Spinner } from './components/Spinner';
import { ResultImage } from './components/ResultImage';
import { generateVirtualStaging, listAvailableModels, testAllModelsForImageGeneration, ModelTestResult } from './services/geminiService';
import { ArrowDownIcon, SparklesIcon } from './components/Icons';

type LoadingStep = 'idle' | 'analyzingStyle' | 'analyzingPlan' | 'generatingImage';

const App: React.FC = () => {
  const [floorPlanImage, setFloorPlanImage] = useState<File | null>(null);
  const [referenceImage, setReferenceImage] = useState<File | null>(null);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [loadingStep, setLoadingStep] = useState<LoadingStep>('idle');
  const [error, setError] = useState<string | null>(null);
  const [availableModels, setAvailableModels] = useState<string[] | null>(null);
  const [modelError, setModelError] = useState<string | null>(null);
  const [modelTestResults, setModelTestResults] = useState<ModelTestResult[] | null>(null);
  const [isTestingModels, setIsTestingModels] = useState(false);

  const handleCheckModels = useCallback(async () => {
    setAvailableModels(null);
    setModelError(null);
    try {
      const models = await listAvailableModels();
      if (models.some(m => m.startsWith('Error'))) {
        setModelError(models.join('\n'));
        setAvailableModels(null);
      } else {
        setAvailableModels(models);
      }
    } catch (err) {
      setModelError(err instanceof Error ? err.message : 'An unknown error occurred.');
    }
  }, []);

  const handleTestAllModels = useCallback(async () => {
    setIsTestingModels(true);
    setModelTestResults(null);
    setModelError(null);
    try {
      const results = await testAllModelsForImageGeneration();
      setModelTestResults(results);
    } catch (err) {
      setModelError(err instanceof Error ? err.message : 'An unknown error occurred while testing models.');
    } finally {
      setIsTestingModels(false);
    }
  }, []);

  const handleGenerate = useCallback(async () => {
    if (!floorPlanImage || !referenceImage) {
      setError('Please upload both a floor plan and a reference image.');
      return;
    }
    setError(null);
    setGeneratedImage(null);

    try {
      await generateVirtualStaging(
        floorPlanImage,
        referenceImage,
        setLoadingStep,
        (imageResult) => {
          setGeneratedImage(imageResult);
          setLoadingStep('idle');
        }
      );
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
      setLoadingStep('idle');
    }
  }, [floorPlanImage, referenceImage]);

  const loadingMessages: Record<LoadingStep, string> = {
    idle: '',
    analyzingStyle: 'Analyzing reference image style...',
    analyzingPlan: 'Analyzing floor plan architecture...',
    generatingImage: 'Generating photorealistic render...',
  };

  const isLoading = loadingStep !== 'idle';

  return (
    <div className="min-h-screen bg-gray-900 text-gray-200 font-sans">
      <Header />
      <main className="container mx-auto p-4 md:p-8">
        <div className="max-w-5xl mx-auto">
          <div className="p-6 mb-8 bg-gray-800/50 rounded-xl shadow-lg border border-gray-700">
            <h2 className="text-2xl font-semibold mb-4 text-center">Model Configuration & Testing</h2>

            {/* Current Model Display */}
            <div className="mb-6 p-4 bg-blue-900/30 border border-blue-500/50 rounded-lg">
              <h3 className="font-bold text-lg mb-2 text-blue-300">Currently Using Model:</h3>
              <p className="font-mono text-xl text-blue-100">gemini-3-pro-image-preview</p>
              <p className="text-sm text-gray-400 mt-2">This is the model configured in geminiService.ts - Best quality image generation model</p>
            </div>

            {/* Test Buttons */}
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              <button
                onClick={handleCheckModels}
                className="flex-1 px-6 py-3 bg-blue-600 text-white font-bold rounded-lg shadow-lg hover:bg-blue-700 transition-all duration-300"
              >
                List Available Models
              </button>
              <button
                onClick={handleTestAllModels}
                disabled={isTestingModels}
                className="flex-1 px-6 py-3 bg-purple-600 text-white font-bold rounded-lg shadow-lg hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-all duration-300"
              >
                {isTestingModels ? (
                  <>
                    <Spinner />
                    <span className="ml-2">Testing Models...</span>
                  </>
                ) : (
                  'Test All Models for Image Generation'
                )}
              </button>
            </div>

            {/* Error Display */}
            {modelError && (
              <div className="mt-4 p-3 bg-red-900/50 border border-red-500 rounded-lg text-red-300 text-left font-mono">
                {modelError}
              </div>
            )}

            {/* Available Models List */}
            {availableModels && (
              <div className="mt-4 p-4 bg-gray-800 rounded-lg text-left">
                <h3 className="font-bold text-lg mb-2 text-green-400">Successfully connected! Available Models:</h3>
                <ul className="list-disc list-inside text-gray-300">
                  {availableModels.map((model, index) => (
                    <li key={index} className="font-mono">{model}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Model Test Results */}
            {modelTestResults && modelTestResults.length > 0 && (
              <div className="mt-4 p-4 bg-gray-800 rounded-lg">
                <h3 className="font-bold text-lg mb-4 text-purple-400">Image Generation Test Results:</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-gray-600">
                        <th className="p-3 font-semibold text-gray-300">Model Name</th>
                        <th className="p-3 font-semibold text-gray-300">Supports Images</th>
                        <th className="p-3 font-semibold text-gray-300">Response Time</th>
                        <th className="p-3 font-semibold text-gray-300">Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      {modelTestResults.map((result, index) => (
                        <tr key={index} className="border-b border-gray-700 hover:bg-gray-700/50">
                          <td className="p-3 font-mono text-sm">{result.modelName}</td>
                          <td className="p-3">
                            {result.supportsImageGeneration ? (
                              <span className="px-3 py-1 bg-green-600 text-white rounded-full text-sm font-bold">✓ YES</span>
                            ) : (
                              <span className="px-3 py-1 bg-red-600 text-white rounded-full text-sm font-bold">✗ NO</span>
                            )}
                          </td>
                          <td className="p-3 text-gray-300">
                            {result.responseTime ? `${(result.responseTime / 1000).toFixed(2)}s` : 'N/A'}
                          </td>
                          <td className="p-3 text-sm text-gray-400">
                            {result.error || 'Success'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="mt-4 p-3 bg-yellow-900/30 border border-yellow-500/50 rounded-lg">
                  <p className="text-yellow-300 text-sm">
                    <strong>Note:</strong> Models marked with "YES" can generate images.
                    {modelTestResults.some(r => r.supportsImageGeneration) && (
                      <> The best model for image generation is: <span className="font-mono font-bold">
                        {modelTestResults.find(r => r.supportsImageGeneration)?.modelName || 'N/A'}
                      </span></>
                    )}
                  </p>
                </div>
              </div>
            )}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <ImageUploader
              id="floor-plan"
              title="Step 1: Upload Floor Plan"
              onImageUpload={setFloorPlanImage}
              disabled={isLoading}
            />
            <ImageUploader
              id="reference-image"
              title="Step 2: Upload Reference Image"
              onImageUpload={setReferenceImage}
              disabled={isLoading}
            />
          </div>

          <div className="text-center mb-8">
            <button
              onClick={handleGenerate}
              disabled={!floorPlanImage || !referenceImage || isLoading}
              className="inline-flex items-center justify-center px-8 py-4 bg-purple-600 text-white font-bold rounded-lg shadow-lg hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 disabled:scale-100"
            >
              {isLoading ? (
                <>
                  <Spinner />
                  <span className="ml-3">{loadingMessages[loadingStep]}</span>
                </>
              ) : (
                <>
                  <SparklesIcon className="w-6 h-6 mr-3" />
                  Generate Virtual Staging
                </>
              )}
            </button>
            {error && <p className="text-red-400 mt-4">{error}</p>}
          </div>

          {generatedImage && !isLoading && (
            <div className="text-center animate-fade-in">
              <ArrowDownIcon className="w-10 h-10 mx-auto text-purple-400 mb-4" />
              <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500 mb-6">Your Render is Ready!</h2>
              <ResultImage src={generatedImage} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
