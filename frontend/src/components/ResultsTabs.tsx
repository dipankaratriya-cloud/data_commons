import React, { useState } from 'react';
import { FileText, MapPin, Calendar, Terminal, ShieldCheck, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface ResultsTabsProps {
    data: any;
}

export function ResultsTabs({ data }: ResultsTabsProps) {
    const [activeTab, setActiveTab] = useState('summary');

    if (!data) return null;

    const parsed = data.parsed_metadata || {};
    const license = parsed.license || {};
    const place = parsed.place || {};
    const temporal = parsed.temporal || {};

    const tabs = [
        { id: 'summary', label: 'Summary', icon: FileText },
        { id: 'license', label: 'License', icon: ShieldCheck },
        { id: 'place', label: 'Place/Geo', icon: MapPin },
        { id: 'temporal', label: 'Temporal', icon: Calendar },
        { id: 'sessions', label: 'Sessions', icon: Terminal },
    ];

    return (
        <div className="w-full bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="flex border-b border-gray-200 overflow-x-auto">
                {tabs.map((tab) => {
                    const Icon = tab.icon;
                    const isActive = activeTab === tab.id;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={cn(
                                "flex items-center gap-2 px-6 py-4 text-sm font-medium transition-colors whitespace-nowrap",
                                isActive
                                    ? "text-blue-600 border-b-2 border-blue-600 bg-blue-50/50"
                                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                            )}
                        >
                            <Icon className="w-4 h-4" />
                            {tab.label}
                        </button>
                    );
                })}
            </div>

            <div className="p-6 min-h-[400px]">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.2 }}
                    >
                        {activeTab === 'summary' && (
                            <div className="prose max-w-none">
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">Complete Extracted Information</h3>
                                <div className="bg-gray-50 rounded-lg p-6 border border-gray-100 text-gray-700 whitespace-pre-wrap leading-relaxed">
                                    {data.content || "No content available"}
                                </div>
                            </div>
                        )}

                        {activeTab === 'license' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-semibold text-gray-900">License Information</h3>

                                {license.license_type || license.license_url ? (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="bg-blue-50 rounded-xl p-6 border border-blue-100">
                                            <div className="text-sm text-blue-600 font-medium mb-1">License Type</div>
                                            <div className="text-2xl font-bold text-blue-900">{license.license_type || "Unknown"}</div>
                                            {license.confidence && (
                                                <div className="mt-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                    Confidence: {license.confidence}
                                                </div>
                                            )}
                                        </div>

                                        <div className="bg-gray-50 rounded-xl p-6 border border-gray-100">
                                            <div className="text-sm text-gray-500 font-medium mb-1">License URL</div>
                                            {license.license_url ? (
                                                <a
                                                    href={license.license_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-blue-600 hover:underline break-all"
                                                >
                                                    {license.license_url}
                                                </a>
                                            ) : (
                                                <span className="text-gray-400">Not available</span>
                                            )}
                                        </div>

                                        {license.attribution && (
                                            <div className="md:col-span-2 bg-indigo-50 rounded-xl p-6 border border-indigo-100 flex gap-4">
                                                <Info className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
                                                <div>
                                                    <h4 className="font-medium text-indigo-900 mb-1">Attribution Requirements</h4>
                                                    <p className="text-indigo-800">{license.attribution}</p>
                                                </div>
                                            </div>
                                        )}

                                        {license.restrictions && (
                                            <div className="md:col-span-2 bg-amber-50 rounded-xl p-6 border border-amber-100 flex gap-4">
                                                <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                                                <div>
                                                    <h4 className="font-medium text-amber-900 mb-1">Usage Restrictions</h4>
                                                    <p className="text-amber-800">{license.restrictions}</p>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-300">
                                        <Info className="w-8 h-8 text-gray-400 mx-auto mb-3" />
                                        <p className="text-gray-500">No license information found in the extracted metadata</p>
                                    </div>
                                )}
                            </div>
                        )}

                        {activeTab === 'place' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-semibold text-gray-900">Geographic & Place Information</h3>

                                <div className="grid grid-cols-1 gap-6">
                                    {place.geographic_coverage && Object.keys(place.geographic_coverage).length > 0 && (
                                        <div className="bg-white rounded-xl border border-gray-200 p-6">
                                            <h4 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
                                                <MapPin className="w-4 h-4 text-gray-500" />
                                                Geographic Coverage
                                            </h4>
                                            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-4">
                                                {Object.entries(place.geographic_coverage).map(([key, value]: [string, any]) => (
                                                    value && (
                                                        <div key={key} className="border-l-2 border-gray-100 pl-4">
                                                            <dt className="text-xs text-gray-500 uppercase tracking-wider mb-1">{key.replace('_', ' ')}</dt>
                                                            <dd className="text-sm font-medium text-gray-900">{value}</dd>
                                                        </div>
                                                    )
                                                ))}
                                            </dl>
                                        </div>
                                    )}

                                    {place.place_types && place.place_types.length > 0 && (
                                        <div className="bg-white rounded-xl border border-gray-200 p-6">
                                            <h4 className="font-medium text-gray-900 mb-4">Place Types</h4>
                                            <div className="flex flex-wrap gap-2">
                                                {place.place_types.map((type: string, idx: number) => (
                                                    <span key={idx} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                                                        {type}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {activeTab === 'temporal' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-semibold text-gray-900">Temporal & Date Range Information</h3>

                                {temporal.coverage_period && (
                                    <div className="bg-white rounded-xl border border-gray-200 p-6">
                                        <h4 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
                                            <Calendar className="w-4 h-4 text-gray-500" />
                                            Coverage Period
                                        </h4>
                                        <div className="grid grid-cols-2 gap-8">
                                            <div>
                                                <div className="text-sm text-gray-500 mb-1">Start Date</div>
                                                <div className="text-lg font-semibold text-gray-900">{temporal.coverage_period.start_date || "N/A"}</div>
                                            </div>
                                            <div>
                                                <div className="text-sm text-gray-500 mb-1">End Date</div>
                                                <div className="text-lg font-semibold text-gray-900">{temporal.coverage_period.end_date || "N/A"}</div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {temporal.update_frequency && (
                                    <div className="bg-blue-50 rounded-xl border border-blue-100 p-6">
                                        <h4 className="font-medium text-blue-900 mb-3">Update Information</h4>
                                        <dl className="space-y-2">
                                            {Object.entries(temporal.update_frequency).map(([key, value]: [string, any]) => (
                                                value && (
                                                    <div key={key} className="flex justify-between">
                                                        <dt className="text-blue-700 capitalize">{key.replace('_', ' ')}</dt>
                                                        <dd className="font-medium text-blue-900">{value}</dd>
                                                    </div>
                                                )
                                            ))}
                                        </dl>
                                    </div>
                                )}
                            </div>
                        )}

                        {activeTab === 'sessions' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-semibold text-gray-900">Browser Automation Details</h3>

                                {data.executed_tools && data.executed_tools.length > 0 ? (
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 px-4 py-2 rounded-lg">
                                            <Terminal className="w-4 h-4" />
                                            Launched {data.executed_tools.length} browser session(s)
                                        </div>

                                        {data.executed_tools.map((tool: any, idx: number) => (
                                            <div key={idx} className="border border-gray-200 rounded-lg overflow-hidden">
                                                <div className="bg-gray-50 px-4 py-2 border-b border-gray-200 flex justify-between items-center">
                                                    <span className="font-mono text-sm font-medium text-gray-700">Session {idx + 1}: {tool.type || 'unknown'}</span>
                                                </div>
                                                <div className="p-4 bg-white">
                                                    <pre className="text-xs text-gray-600 overflow-x-auto whitespace-pre-wrap font-mono max-h-40">
                                                        {tool.output ? (typeof tool.output === 'string' ? tool.output.slice(0, 500) : JSON.stringify(tool.output).slice(0, 500)) : 'No output'}
                                                    </pre>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-300">
                                        <p className="text-gray-500">No browser session data available</p>
                                    </div>
                                )}

                                {data.reasoning && (
                                    <div className="mt-8">
                                        <h4 className="font-medium text-gray-900 mb-3">Reasoning Process</h4>
                                        <div className="bg-gray-900 text-gray-300 p-6 rounded-xl font-mono text-sm whitespace-pre-wrap leading-relaxed">
                                            {data.reasoning}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    );
}
