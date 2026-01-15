import React, { useState } from 'react';
import { Search, ArrowRight, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface UrlInputProps {
    onSubmit: (url: string) => void;
    isLoading: boolean;
}

export function UrlInput({ onSubmit, isLoading }: UrlInputProps) {
    const [url, setUrl] = useState('');
    const [isFocused, setIsFocused] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (url.trim()) {
            onSubmit(url.trim());
        }
    };

    return (
        <div className="w-full max-w-3xl mx-auto">
            <form onSubmit={handleSubmit} className="relative group">
                <div className={cn(
                    "absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl opacity-20 group-hover:opacity-40 transition duration-500 blur",
                    isFocused && "opacity-60 group-hover:opacity-80"
                )} />
                <div className="relative flex items-center bg-white rounded-xl shadow-xl border border-gray-100 p-2">
                    <div className="pl-4 pr-3 text-gray-400">
                        <Search className="w-5 h-5" />
                    </div>
                    <input
                        type="url"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        onFocus={() => setIsFocused(true)}
                        onBlur={() => setIsFocused(false)}
                        placeholder="Enter dataset URL to analyze (e.g., https://data.gouv.fr/...)"
                        className="flex-1 bg-transparent border-none outline-none text-gray-900 placeholder-gray-400 text-lg h-12"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !url.trim()}
                        className={cn(
                            "flex items-center gap-2 px-6 h-12 rounded-lg font-semibold text-white transition-all duration-200",
                            isLoading || !url.trim()
                                ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                                : "bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-600/20 hover:shadow-blue-600/30"
                        )}
                    >
                        {isLoading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                <span>Processing</span>
                            </>
                        ) : (
                            <>
                                <span>Analyze</span>
                                <ArrowRight className="w-5 h-5" />
                            </>
                        )}
                    </button>
                </div>
            </form>

            <div className="mt-4 flex items-center justify-center gap-4 text-sm text-gray-500">
                <span>Try examples:</span>
                <button
                    onClick={() => setUrl('https://data.gouv.fr')}
                    className="px-3 py-1 bg-gray-50 hover:bg-gray-100 rounded-full border border-gray-200 transition-colors"
                >
                    data.gouv.fr
                </button>
                <button
                    onClick={() => setUrl('https://www.statcan.gc.ca')}
                    className="px-3 py-1 bg-gray-50 hover:bg-gray-100 rounded-full border border-gray-200 transition-colors"
                >
                    statcan.gc.ca
                </button>
            </div>
        </div>
    );
}
