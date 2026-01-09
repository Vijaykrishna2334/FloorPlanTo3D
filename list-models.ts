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

const listModels = async (apiKey: string, keyName: string) => {
    log(`\n${"=".repeat(60)}`);
    log(`Listing models for ${keyName}: ${apiKey.substring(0, 20)}...`);
    log("=".repeat(60));

    try {
        const ai = new GoogleGenAI({ apiKey });

        log("\n📋 Fetching available models...");
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`);
        const data: any = await response.json();

        if (data.models) {
            log(`\n✅ Found ${data.models.length} models:\n`);
            data.models.forEach((model: any) => {
                const methods = model.supportedGenerationMethods?.join(", ") || "none";
                log(`📦 ${model.name}`);
                log(`   Display Name: ${model.displayName}`);
                log(`   Methods: ${methods}`);
                log(`   Description: ${model.description?.substring(0, 100) || "N/A"}`);
                log("");
            });
        } else if (data.error) {
            log(`❌ Error: ${JSON.stringify(data.error)}`);
        } else {
            log(`⚠️  Unexpected response format`);
        }

    } catch (err) {
        const errorMsg = err instanceof Error ? err.message : JSON.stringify(err);
        log(`❌ Failed to list models: ${errorMsg}`);
    }
};

// Run tests
(async () => {
    log("\n🚀 Listing Available Models for Both API Keys...\n");

    await listModels(API_KEY_1, "API Key #1");
    await listModels(API_KEY_2, "API Key #2");

    log("\n" + "=".repeat(60));
    log("✨ Listing Complete!");
    log("=".repeat(60) + "\n");

    // Save results to file
    fs.writeFileSync("models-list.txt", results);
    log("\n📝 Results saved to models-list.txt");
})();
