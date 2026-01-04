'use client';
import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Trash2, Send, Key, FileText, CheckCircle2, Sparkles, Settings, Camera, Image as ImageIcon, X } from 'lucide-react';

export default function Home() {
    const [samples, setSamples] = useState(['']); // Start with one empty sample
    const [sampleImages, setSampleImages] = useState([]); // Base64 strings
    const [prompt, setPrompt] = useState('');
    const [apiKey, setApiKey] = useState('');
    const [generatedLetter, setGeneratedLetter] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    const [error, setError] = useState('');

    const fileInputRef = useRef(null);

    const addSample = () => setSamples([...samples, '']);
    const removeSample = (index) => {
        if (samples.length > 1) {
            setSamples(samples.filter((_, i) => i !== index));
        }
    };

    const updateSample = (index, value) => {
        const newSamples = [...samples];
        newSamples[index] = value;
        setSamples(newSamples);
    };

    // Image Handling
    const handleImageUpload = (e) => {
        const files = e.target.files;
        if (files) {
            Array.from(files).forEach(file => {
                const reader = new FileReader();
                reader.onloadend = () => {
                    setSampleImages(prev => [...prev, reader.result]);
                };
                reader.readAsDataURL(file);
            });
        }
    };

    const removeImage = (index) => {
        setSampleImages(prev => prev.filter((_, i) => i !== index));
    };

    const handleGenerate = async () => {
        setIsLoading(true);
        setGeneratedLetter('');
        setError('');

        try {
            const validSamples = samples.filter(s => s.trim().length > 0);
            // Valid if we have TEXT samples OR IMAGE samples OR just a prompt
            if (!prompt.trim()) throw new Error("Please enter a prompt for the new letter.");

            // Use production URL if available, otherwise local proxy
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || '';
            const response = await fetch(`${baseUrl}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    samples: validSamples,
                    sample_images: sampleImages,
                    target_prompt: prompt,
                    api_key: apiKey || 'mock'
                }),
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || data.letter || "Generation failed");

            setGeneratedLetter(data.letter);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="app-container">
            {/* Navigation Bar */}
            <nav className="navbar">
                <div className="nav-content">
                    <div className="brand">
                        <div className="logo-icon">
                            <Sparkles size={20} color="white" />
                        </div>
                        <h1 className="title-text">
                            GhostWriter AI
                        </h1>
                    </div>

                    <div style={{ position: 'relative' }}>
                        <button
                            onClick={() => setShowSettings(!showSettings)}
                            className="settings-btn"
                        >
                            <Settings size={18} />
                            <span>API Key</span>
                        </button>

                        {/* Settings Dropdown */}
                        <AnimatePresence>
                            {showSettings && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="settings-overlay glass-panel"
                                >
                                    <label style={{ display: 'block', color: 'var(--text-main)', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '500' }}>
                                        Gemini API Key
                                    </label>
                                    <input
                                        type="password"
                                        value={apiKey}
                                        onChange={(e) => setApiKey(e.target.value)}
                                        placeholder="AIza..."
                                        className="input-field"
                                        style={{ background: 'white' }}
                                    />
                                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem', lineHeight: '1.4' }}>
                                        Required for Image Analysis (Gemini). Leave empty for Mock Mode.
                                    </p>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </nav>

            <div className="main-content">
                <div className="main-grid">

                    {/* Left Column: Input */}
                    <div className="input-section">

                        {/* 1. Text Samples */}
                        <section>
                            <div className="section-label">
                                <FileText size={16} color="var(--primary)" />
                                Text Samples <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>(Optional)</span>
                            </div>

                            <div className="sample-list">
                                <AnimatePresence>
                                    {samples.map((sample, index) => (
                                        <motion.div
                                            key={index}
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, scale: 0.95 }}
                                            className="input-wrapper"
                                        >
                                            <textarea
                                                value={sample}
                                                onChange={(e) => updateSample(index, e.target.value)}
                                                placeholder={`Paste sample text...`}
                                                className="input-field"
                                                style={{ minHeight: '100px' }}
                                            />
                                            {samples.length > 1 && (
                                                <button
                                                    onClick={() => removeSample(index)}
                                                    className="delete-btn"
                                                    title="Remove"
                                                >
                                                    <Trash2 size={16} />
                                                </button>
                                            )}
                                        </motion.div>
                                    ))}
                                </AnimatePresence>
                            </div>

                            <button
                                onClick={addSample}
                                className="add-btn"
                                style={{ marginTop: '1rem' }}
                            >
                                <Plus size={16} />
                                Add Text Block
                            </button>
                        </section>

                        {/* 2. Image Samples */}
                        <section>
                            <div className="section-label">
                                <ImageIcon size={16} color="var(--primary)" />
                                Image Samples <span className="sample-count">{sampleImages.length}</span>
                            </div>

                            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                                {sampleImages.map((img, idx) => (
                                    <div key={idx} style={{ position: 'relative', width: '80px', height: '80px', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--border)' }}>
                                        <img src={img} alt="sample" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                        <button
                                            onClick={() => removeImage(idx)}
                                            style={{ position: 'absolute', top: 2, right: 2, background: 'rgba(0,0,0,0.5)', color: 'white', borderRadius: '50%', border: 'none', padding: 2, cursor: 'pointer', display: 'flex' }}
                                        >
                                            <X size={12} />
                                        </button>
                                    </div>
                                ))}
                            </div>

                            <div style={{ display: 'flex', gap: '1rem' }}>
                                <input
                                    type="file"
                                    accept="image/*"
                                    multiple
                                    ref={fileInputRef}
                                    style={{ display: 'none' }}
                                    onChange={handleImageUpload}
                                />
                                <button
                                    onClick={() => fileInputRef.current.click()}
                                    className="add-btn"
                                    style={{ flex: 1 }}
                                >
                                    <ImageIcon size={16} />
                                    Upload Photos
                                </button>

                                {/* Mobile Camera Trigger */}
                                <button
                                    onClick={() => fileInputRef.current.click()} // Same trigger, mobile will toggle camera option
                                    className="add-btn"
                                    style={{ flex: 1 }}
                                >
                                    <Camera size={16} />
                                    Capture
                                </button>
                            </div>
                        </section>

                        <section>
                            <h2 className="section-label">
                                <Send size={16} color="var(--secondary)" />
                                Target Prompt
                            </h2>
                            <textarea
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                placeholder="e.g. Write a resignation letter..."
                                className="input-field prompt-area"
                            />
                        </section>

                        {error && (
                            <div className="error-msg">
                                {error}
                            </div>
                        )}

                        <button
                            onClick={handleGenerate}
                            disabled={isLoading}
                            className="generate-btn"
                        >
                            {isLoading ? (
                                <>
                                    <div className="spinner" />
                                    Analyzing...
                                </>
                            ) : (
                                <>
                                    Generate Draft
                                    <Sparkles size={18} />
                                </>
                            )}
                        </button>
                    </div>

                    {/* Right Column: Output */}
                    <div className="output-section">
                        <div className="glass-panel output-container">
                            <h2 className="section-label" style={{ marginBottom: '1rem' }}>Generated Draft</h2>

                            {generatedLetter ? (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="output-content custom-scrollbar"
                                >
                                    {generatedLetter}
                                </motion.div>
                            ) : (
                                <div className="empty-state">
                                    <div className="empty-icon">
                                        <FileText size={48} strokeWidth={1} />
                                    </div>
                                    <p>
                                        Draft will appear here.
                                    </p>
                                </div>
                            )}

                            {generatedLetter && (
                                <div className="copy-actions">
                                    <button
                                        onClick={() => navigator.clipboard.writeText(generatedLetter)}
                                        className="copy-btn"
                                    >
                                        <CheckCircle2 size={18} />
                                        Copy
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>

                </div>
            </div>
        </main>
    );
}
