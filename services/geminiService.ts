
import { GoogleGenAI, Part } from "@google/genai";
import { fileToBase64 } from "../utils/fileUtils";
import { STYLE_EXTRACTION_PROMPT, FLOOR_PLAN_ANALYSIS_PROMPT, getFinalPromptTemplate } from "../constants";

const API_KEY = import.meta.env.VITE_GEMINI_API_KEY;

if (!API_KEY) {
  throw new Error("VITE_GEMINI_API_KEY environment variable is not set.");
}

const ai = new GoogleGenAI({ apiKey: API_KEY });
// Updated to use image generation model - gemini-3-pro-image-preview is the best quality image generation model
const model = "gemini-3-pro-image-preview";

type LoadingStep = 'idle' | 'analyzingStyle' | 'analyzingPlan' | 'generatingImage';
type SetLoadingStep = (step: LoadingStep) => void;
type OnResult = (result: string) => void;

async function fileToGenerativePart(file: File): Promise<Part> {
  const base64EncodedData = await fileToBase64(file);
  return {
    inlineData: {
      data: base64EncodedData,
      mimeType: file.type,
    },
  };
}

export const generateVirtualStaging = async (
  floorPlanFile: File,
  referenceImageFile: File,
  setLoadingStep: SetLoadingStep,
  onResult: OnResult
) => {
  // Step 1: Analyze Reference Image Style
  setLoadingStep('analyzingStyle');
  const referenceImagePart = await fileToGenerativePart(referenceImageFile);
  const styleResponse = await ai.models.generateContent({
    model: model,
    contents: [{ parts: [{ text: STYLE_EXTRACTION_PROMPT }, referenceImagePart] }]
  });
  const styleDescription = styleResponse.text;
  if (!styleDescription) throw new Error("Could not extract style from reference image.");

  // Step 2: Analyze Floor Plan Architecture
  setLoadingStep('analyzingPlan');
  const floorPlanPart = await fileToGenerativePart(floorPlanFile);
  const floorPlanResponse = await ai.models.generateContent({
    model: model,
    contents: [{ parts: [{ text: FLOOR_PLAN_ANALYSIS_PROMPT }, floorPlanPart] }]
  });
  const floorPlanAnalysis = floorPlanResponse.text;
  if (!floorPlanAnalysis) throw new Error("Could not analyze the floor plan image.");

  // Step 3: Construct Final Prompt and Generate Image
  setLoadingStep('generatingImage');
  const finalPrompt = getFinalPromptTemplate(styleDescription, floorPlanAnalysis);

  const finalResponse = await ai.models.generateContent({
    model: model,
    contents: {
      parts: [
        floorPlanPart,
        { text: finalPrompt },
      ],
    },
  });

  // Extract the generated image
  for (const part of finalResponse.candidates?.[0]?.content?.parts || []) {
    if (part.inlineData) {
      const base64Data = part.inlineData.data;
      const mimeType = part.inlineData.mimeType;
      onResult(`data:${mimeType};base64,${base64Data}`);
      return;
    }
  }

  throw new Error("No image was generated. The model may have refused the request.");
};

export const listAvailableModels = async () => {
  try {
    const models = await ai.models.list();
    const modelNames = [];
    for (const model of models) {
      // We only care about models that can be used for content generation
      if (model.supportedGenerationMethods.includes('generateContent')) {
        modelNames.push(model.name);
      }
    }
    if (modelNames.length === 0) {
      return ["No models supporting 'generateContent' found for your API key."];
    }
    return modelNames;
  } catch (err) {
    console.error("Error listing models:", err);
    if (err instanceof Error) {
      return [`Error listing models: ${err.message}`];
    }
    return ["An unknown error occurred while listing models."];
  }
};

export interface ModelTestResult {
  modelName: string;
  supportsImageGeneration: boolean;
  error?: string;
  responseTime?: number;
}

export const testImageGenerationModel = async (modelName: string): Promise<ModelTestResult> => {
  const startTime = Date.now();
  try {
    // Create a simple test prompt for image generation
    const testPrompt = "Generate a simple geometric shape: a blue circle on a white background.";

    const response = await ai.models.generateContent({
      model: modelName,
      contents: {
        parts: [{ text: testPrompt }],
      },
    });

    const responseTime = Date.now() - startTime;

    // Check if the response contains an image
    const hasImage = response.candidates?.[0]?.content?.parts?.some(
      part => part.inlineData !== undefined
    );

    if (hasImage) {
      return {
        modelName,
        supportsImageGeneration: true,
        responseTime,
      };
    } else {
      return {
        modelName,
        supportsImageGeneration: false,
        error: "Model responded but did not generate an image",
        responseTime,
      };
    }
  } catch (err) {
    const responseTime = Date.now() - startTime;
    return {
      modelName,
      supportsImageGeneration: false,
      error: err instanceof Error ? err.message : "Unknown error",
      responseTime,
    };
  }
};

export const testAllModelsForImageGeneration = async (): Promise<ModelTestResult[]> => {
  const models = await listAvailableModels();

  // Filter out error messages
  const validModels = models.filter(m => !m.startsWith('Error') && !m.startsWith('No models'));

  if (validModels.length === 0) {
    return [];
  }

  const results: ModelTestResult[] = [];

  for (const modelName of validModels) {
    console.log(`Testing model: ${modelName}`);
    const result = await testImageGenerationModel(modelName);
    results.push(result);
  }

  return results;
};
