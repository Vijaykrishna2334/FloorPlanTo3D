import { GoogleGenAI } from "@google/genai";
import * as fs from "fs";

// Test both API keys
const API_KEY_1 = "AIzaSyBGLEwaWgETC6mHAOJhzIMVjqGstbBGQzs";
const API_KEY_2 = "AIzaSyAwIn-9Gv6Chvwsp1KDr9OKNKIBiN2qSZc";

let results = "";

const log = (message: string) => {
    console.log(message);
    results += message + "\n";
};

const testApiKey = async (apiKey: string, keyName: string) => {
    log(`\n${"=".repeat(60)}`);
    log(`Testing ${keyName}: ${apiKey.substring(0, 20)}...`);
    log("=".repeat(60));

    try {
        const ai = new GoogleGenAI({ apiKey });

        // Test image generation with gemini-1.5-flash (current model)
        log("\n🎨 Testing image generation with gemini-1.5-flash...");
        try {
            const response = await ai.models.generateContent({
                model: "gemini-1.5-flash",
                contents: {
                    parts: [{ text: "Generate a simple blue circle on white background." }],
                },
            });

            const hasImage = response.candidates?.[0]?.content?.parts?.some(
                part => part.inlineData !== undefined
            );

            if (hasImage) {
                log("✅ gemini-1.5-flash CAN generate images!");
            } else {
                log("❌ gemini-1.5-flash responded but did NOT generate an image");
                log("Response text: " + (response.text?.substring(0, 200) || "No text"));
            }
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : JSON.stringify(err);
            log("❌ gemini-1.5-flash FAILED: " + errorMsg);
        }

    } catch (err) {
        const errorMsg = err instanceof Error ? err.message : JSON.stringify(err);
        log("❌ API Key Test FAILED: " + errorMsg);
    }
};

// Run tests
(async () => {
    log("\n🚀 Starting API Key and Model Tests...\n");

    await testApiKey(API_KEY_1, "API Key #1");
    await testApiKey(API_KEY_2, "API Key #2");

    log("\n" + "=".repeat(60));
    log("✨ Testing Complete!");
    log("=".repeat(60) + "\n");

    // Save results to file
    fs.writeFileSync("test-results.txt", results);
    log("\n📝 Results saved to test-results.txt");
})();
