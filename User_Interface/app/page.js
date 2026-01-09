'use client';
import { useState, useEffect, useRef } from 'react';
import { createWorker } from 'tesseract.js';
import { Shield, ShieldCheck, Lock, Upload, FileText, Activity, RefreshCw, Send, Check } from 'lucide-react';

export default function Home() {
    const [ocrStatus, setOcrStatus] = useState('idle'); // idle, recognizing, done
    const [ocrProgress, setOcrProgress] = useState(0);
    const [extractedText, setExtractedText] = useState('');

    const [prompt, setPrompt] = useState('');
    // const [apiKey, setApiKey] = useState(''); // REPLACED BY .ENV IN BACKEND

    const [generatedLetter, setGeneratedLetter] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [debugInfo, setDebugInfo] = useState(null);

    // Local OCR Handler
    const processImageLocally = async (imageFile) => {
        setOcrStatus('recognizing');
        setOcrProgress(0);

        const worker = await createWorker();

        // Tesseract.js logger to track progress
        await worker.loadLanguage('eng');
        await worker.initialize('eng');

        const { data: { text } } = await worker.recognize(imageFile);

        setExtractedText(prev => prev + (prev ? '\n\n' : '') + text);
        setOcrStatus('done');
        setOcrProgress(100);

        await worker.terminate();
    };

    const handleFileChange = (e) => {
        if (e.target.files?.[0]) {
            processImageLocally(e.target.files[0]);
        }
    };

    const handleGenerate = async () => {
        if (!prompt) return;
        setIsGenerating(true);
        setGeneratedLetter('');
        setDebugInfo(null);

        try {
            const response = await fetch('http://localhost:8000/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text_content: extractedText,
                    target_prompt: prompt
                })
            });

            const data = await response.json();
            if (response.ok) {
                setGeneratedLetter(data.letter);
                setDebugInfo({
                    sent: data.debug_anonymized_sent,
                    map_count: data.debug_map_count
                });
            } else {
                alert("Error: " + data.detail);
            }
        } catch (e) {
            alert("Network Error: " + e.message);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0f172a] text-white font-sans selection:bg-green-500 selection:text-white">
            {/* Header */}
            <header className="border-b border-white/10 bg-[#0f172a]/50 backdrop-blur-md sticky top-0 z-10">
                <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-green-400">
                        <ShieldCheck size={24} />
                        <h1 className="font-bold text-lg tracking-tight text-white">Letter Engine <span className="text-xs font-normal text-white/50 border border-white/20 px-2 py-0.5 rounded-full ml-2">AI Letter Generator</span></h1>
                    </div>
                </div>
            </header>

            <main className="max-w-5xl mx-auto px-6 py-12 grid grid-cols-1 lg:grid-cols-2 gap-12">

                {/* Left Col: Input & Local Processing */}
                <section className="space-y-8">

                    {/* 1. Reference Material Upload */}
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-50 group-hover:opacity-100 transition-opacity">
                            <Upload size={16} className="text-green-400" />
                        </div>

                        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                            <Upload size={20} className="text-blue-400" />
                            Reference Material
                        </h2>

                        <div className="mb-6 p-4 rounded-xl border border-dashed border-white/20 hover:border-blue-400/50 hover:bg-blue-400/5 transition-all text-center cursor-pointer relative">
                            <input
                                type="file"
                                onChange={handleFileChange}
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                accept="image/*"
                            />
                            <div className="py-4">
                                <p className="text-blue-300 font-medium">Drop an image</p>
                                <p className="text-xs text-white/40 mt-1"></p>
                            </div>
                        </div>

                        {/* OCR Progress / Result */}
                        {(ocrStatus !== 'idle' || extractedText) && (
                            <div className="bg-black/30 rounded-lg p-3 text-sm font-mono border border-white/5">
                                {ocrStatus === 'recognizing' && (
                                    <div className="flex items-center gap-3 text-yellow-400">
                                        <RefreshCw size={14} className="animate-spin" />
                                        <span>Reading Image... {extractProgress(ocrProgress)}%</span>
                                    </div>
                                )}
                                {extractedText && (
                                    <div className="space-y-2">
                                        <div className="flex items-center justify-between text-green-400 text-xs uppercase tracking-wider mb-2">
                                            <span>Extracted Content</span>
                                            <Shield size={12} />
                                        </div>
                                        <textarea
                                            value={extractedText}
                                            onChange={(e) => setExtractedText(e.target.value)}
                                            className="w-full bg-transparent text-white/80 outline-none resize-none h-32 text-xs"
                                            placeholder="Or type/paste text manually here..."
                                        />
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* 2. Target Prompt */}
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                            <Send size={20} className="text-purple-400" />
                            Your Instruction
                        </h2>
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="e.g. Write a letter to John Smith refusing his refund request..."
                            className="w-full bg-black/20 border border-white/10 rounded-xl p-4 text-white placeholder:text-white/20 focus:border-purple-400/50 outline-none min-h-[120px] transition-all"
                        />

                        {/* API Key Managed via .env now */}

                        <button
                            onClick={handleGenerate}
                            disabled={isGenerating || !prompt}
                            className="mt-6 w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-medium py-3 rounded-xl transition-all shadow-lg shadow-purple-900/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                        >
                            {isGenerating ? (
                                <>
                                    <Activity size={18} className="animate-pulse" />
                                    Analyzing & Generating...
                                </>
                            ) : (
                                <>
                                    Generate Letter
                                    <Send size={18} />
                                </>
                            )}
                        </button>
                    </div>
                </section>

                {/* Right Col: Output */}
                <section className="bg-white/5 border border-white/10 rounded-2xl p-8 flex flex-col h-full min-h-[500px]">
                    <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 border-b border-white/10 pb-4">
                        <FileText size={20} className="text-green-400" />
                        Generated Draft
                    </h2>

                    <div className="flex-1 font-serif text-lg leading-relaxed text-white/90 whitespace-pre-wrap">
                        {generatedLetter || (
                            <span className="text-white/20 italic">
                                Generated content will appear here.
                                <br /><br />
                                1. Upload a sample.
                                <br />
                                2. Enter new instructions.
                                <br />
                                3. Get a result in your style.
                            </span>
                        )}
                    </div>
                </section>

            </main>
        </div>
    );
}

function extractProgress(val) {
    return Math.floor(val || 0);
}
