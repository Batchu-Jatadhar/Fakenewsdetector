"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { analysisAPI } from "@/lib/api";

export default function SubmitForm() {
  const router = useRouter();
  const [inputType, setInputType] = useState<"text" | "url">("text");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) {
      setError("Please enter content to analyze");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await analysisAPI.analyze({
        input_type: inputType,
        content: content.trim(),
      });
      router.push(`/results/${response.data.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Input Type Toggle */}
      <div className="flex bg-surface rounded-lg p-1 w-fit">
        <button
          type="button"
          onClick={() => setInputType("text")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            inputType === "text"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Paste Text
        </button>
        <button
          type="button"
          onClick={() => setInputType("url")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            inputType === "url"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Enter URL
        </button>
      </div>

      {/* Input Area */}
      {inputType === "text" ? (
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste the news article or claim text here for analysis..."
          className="input-field h-48 resize-y"
          disabled={loading}
        />
      ) : (
        <input
          type="url"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="https://example.com/news-article"
          className="input-field"
          disabled={loading}
        />
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading || !content.trim()}
        className="btn-primary w-full flex items-center justify-center space-x-2"
      >
        {loading ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span>Analyzing with AI...</span>
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span>Analyze Content</span>
          </>
        )}
      </button>
    </form>
  );
}
