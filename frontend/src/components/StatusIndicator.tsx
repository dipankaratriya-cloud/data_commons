import React from 'react';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatusIndicatorProps {
    status: 'idle' | 'loading' | 'success' | 'error';
    message?: string;
}

export function StatusIndicator({ status, message }: StatusIndicatorProps) {
    if (status === 'idle') return null;

    return (
        <div className={cn(
            "w-full max-w-3xl mx-auto mb-8 p-4 rounded-xl flex items-center gap-3 animate-in fade-in slide-in-from-bottom-4 duration-300",
            status === 'loading' && "bg-blue-50 border border-blue-100 text-blue-700",
            status === 'success' && "bg-green-50 border border-green-100 text-green-700",
            status === 'error' && "bg-red-50 border border-red-100 text-red-700"
        )}>
            {status === 'loading' && <Loader2 className="w-5 h-5 animate-spin flex-shrink-0" />}
            {status === 'success' && <CheckCircle2 className="w-5 h-5 flex-shrink-0" />}
            {status === 'error' && <AlertCircle className="w-5 h-5 flex-shrink-0" />}

            <div className="flex-1 font-medium">
                {message || (
                    status === 'loading' ? 'Processing request...' :
                        status === 'success' ? 'Extraction completed successfully' :
                            'An error occurred'
                )}
            </div>
        </div>
    );
}
