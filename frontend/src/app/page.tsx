'use client';

import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { UrlInput } from '@/components/UrlInput';
import { ResultsTabs } from '@/components/ResultsTabs';
import { StatusIndicator } from '@/components/StatusIndicator';
import axios from 'axios';

export default function Home() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [statusMessage, setStatusMessage] = useState('');
  const [data, setData] = useState<any>(null);

  const handleExtract = async (url: string) => {
    setStatus('loading');
    setStatusMessage('Initializing browser automation (this may take up to 4 minutes)...');
    setData(null);

    try {
      const response = await axios.post('/api/extract', { url });

      if (response.data.success) {
        setData(response.data);
        setStatus('success');
        setStatusMessage(`Successfully extracted metadata from ${url}`);
      } else {
        setStatus('error');
        setStatusMessage(response.data.error || 'Extraction failed');
      }
    } catch (error: any) {
      setStatus('error');
      setStatusMessage(error.response?.data?.error || error.message || 'An unexpected error occurred');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-4">
            Unlock Dataset Intelligence
          </h2>
          <p className="text-xl text-gray-500 max-w-2xl mx-auto">
            Automated metadata extraction powered by advanced browser automation.
            Get license, geographic, and temporal insights in seconds.
          </p>
        </div>

        <div className="mb-12">
          <UrlInput onSubmit={handleExtract} isLoading={status === 'loading'} />
        </div>

        <StatusIndicator status={status} message={statusMessage} />

        {data && <ResultsTabs data={data} />}
      </main>
    </div>
  );
}
