import React from 'react';
import { Database } from 'lucide-react';

export function Header() {
    return (
        <header className="w-full border-b border-gray-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-600 rounded-lg shadow-lg shadow-blue-600/20">
                        <Database className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900 tracking-tight">Metadata Extractor</h1>
                        <p className="text-xs text-gray-500 font-medium">Enterprise Edition</p>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    <div className="text-sm text-gray-500">
                        <span className="w-2 h-2 bg-green-500 rounded-full inline-block mr-2 animate-pulse"></span>
                        System Operational
                    </div>
                </div>
            </div>
        </header>
    );
}
