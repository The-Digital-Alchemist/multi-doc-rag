"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Key, Lock, Eye, EyeOff, ShieldCheck, AlertCircle, ChevronDown, ChevronUp } from "lucide-react";

interface ApiKeyModalProps {
  isOpen: boolean;
  onSubmit: (apiKey: string) => void;
  error?: string;
}

export function ApiKeyModal({ isOpen, onSubmit, error }: ApiKeyModalProps) {
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (apiKey.trim()) {
      onSubmit(apiKey.trim());
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <Card className="w-full max-w-lg shadow-2xl border-gray-200 bg-white animate-fade-in">
        <CardHeader className="pb-4 border-b border-gray-100">
          <CardTitle className="flex items-center gap-3 text-xl">
            <div className="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center">
              <Key className="h-5 w-5 text-blue-600" />
            </div>
            <span>OpenAI API Key Required</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-6 space-y-6">
          {/* Trust Badges */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-3">
            <div className="flex items-start gap-3">
              <Lock className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-green-900">
                  Your API key is never stored or saved
                </p>
                <p className="text-xs text-green-700 mt-1">
                  We only hold your key in memory during your browser session
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <ShieldCheck className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-green-900">
                  No logging or persistence
                </p>
                <p className="text-xs text-green-700 mt-1">
                  Your credentials are never written to disk or databases
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-green-900">
                  Direct to OpenAI only
                </p>
                <p className="text-xs text-green-700 mt-1">
                  Your key is only transmitted directly to OpenAI&apos;s API
                </p>
              </div>
            </div>
          </div>

          {/* Why do I need this? */}
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <button
              type="button"
              onClick={() => setShowExplanation(!showExplanation)}
              className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between text-left"
            >
              <span className="text-sm font-medium text-gray-700">
                Why do I need to provide my API key?
              </span>
              {showExplanation ? (
                <ChevronUp className="h-4 w-4 text-gray-500" />
              ) : (
                <ChevronDown className="h-4 w-4 text-gray-500" />
              )}
            </button>
            {showExplanation && (
              <div className="px-4 py-3 bg-white border-t border-gray-200 space-y-2 text-sm text-gray-600">
                <p>
                  This is a <strong>Bring Your Own Key (BYOK)</strong> demo. You maintain full control over your OpenAI usage and costs.
                </p>
                <p className="mt-2">
                  <strong>Benefits:</strong>
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>You control your spending and rate limits</li>
                  <li>Your data stays between you and OpenAI</li>
                  <li>No third-party API key management</li>
                  <li>Complete transparency in AI operations</li>
                </ul>
                <p className="mt-2 text-xs text-gray-500">
                  Get your API key from{" "}
                  <a
                    href="https://platform.openai.com/api-keys"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    platform.openai.com/api-keys
                  </a>
                </p>
              </div>
            )}
          </div>

          {/* API Key Input */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="api-key" className="text-sm font-medium text-gray-700">
                Enter your OpenAI API Key
              </label>
              <div className="relative">
                <Input
                  id="api-key"
                  type={showKey ? "text" : "password"}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="pr-10 font-mono text-sm"
                  autoFocus
                />
                <button
                  type="button"
                  onClick={() => setShowKey(!showKey)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showKey ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg animate-fade-in">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <Button
              type="submit"
              disabled={!apiKey.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white h-11"
            >
              Continue to Cortex
            </Button>
          </form>

          <p className="text-xs text-center text-gray-500">
            Refreshing the page will require you to re-enter your API key
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

