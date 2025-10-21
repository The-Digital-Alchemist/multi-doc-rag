"use client";

import { useState } from "react";
type SourceItem = { content: string; score: number; doc_id: string; source_filename: string };
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Upload, Search, FileText, Loader2, ChevronDown, ChevronUp, Trash2, File } from "lucide-react";
import { apiService } from "@/lib/api";
import { sessionManager } from "@/lib/session";

export default function Home() {
  const [query, setQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [searchError, setSearchError] = useState("");
  const [showSources, setShowSources] = useState(true);
  const [sessionId, setSessionId] = useState<string>(sessionManager.getSessionId());

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    setIsUploading(true);
    setUploadError("");


    try {
      for (const file of files) {
        await apiService.uploadFile(file, sessionId);
        setUploadedFiles(prev => [...prev, file.name])
      }
    } catch{
      setUploadError("Upload failed. Something went wrong.")
    } finally {
      setIsUploading(false);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsSearching(true);
    setAnswer("");
    setSources([]);
    setSearchError("");
    setShowSources(true);

    try {
      const response = await apiService.queryDocuments(query, sessionId);
      setAnswer(response.answer);
      setSources(response.results || []);
    } catch{ 
      setSearchError("Search failed. Something went wrong.")
    } finally {
      setIsSearching(false);
    }
  };

  const handleClearFiles = () => {
    // Clear current session and generate new one
    sessionManager.clearSession();
    const newSessionId = sessionManager.getSessionId();
    setSessionId(newSessionId);
    
    // Clear UI state
    setUploadedFiles([]);
    setAnswer("");
    setSources([]);
    setQuery("");
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return '📄';
    if (ext === 'docx') return '📝';
    if (ext === 'txt') return '📃';
    return '📄';
  };

  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Header - Sticky */}
      <header className="sticky top-0 z-10 bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Cortex</h1>
              <p className="text-sm text-gray-500 mt-2">
                Upload documents and ask questions powered by AI
              </p>
            </div>
            {uploadedFiles.length > 0 && (
              <div className="flex items-center gap-4">
                <Badge variant="secondary" className="text-sm px-3 py-1">
                  {uploadedFiles.length} {uploadedFiles.length === 1 ? 'document' : 'documents'}
                </Badge>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-10 max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Section - Sidebar */}
          <div className="lg:col-span-1">
            <Card className="shadow-sm border-gray-200 bg-white">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center justify-between text-lg">
                  <div className="flex items-center gap-2">
                    <Upload className="h-5 w-5 text-blue-600" />
                    <span>Documents</span>
                  </div>
                  {uploadedFiles.length > 0 && (
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={handleClearFiles}
                      className="h-8 text-xs text-gray-500 hover:text-red-600"
                    >
                      <Trash2 className="h-3 w-3 mr-1" />
                      Clear all
                    </Button>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border-2 border-dashed border-gray-200 rounded-xl p-6 text-center hover:border-blue-300 hover:bg-blue-50/30 transition-all">
                  <div className="mb-3">
                    <div className="mx-auto w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center">
                      <FileText className="h-6 w-6 text-blue-600" />
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">
                    PDF, DOCX, or TXT files
                  </p>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.docx,.txt"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <Button 
                    asChild 
                    disabled={isUploading}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                    size="sm"
                  >
                    <label htmlFor="file-upload" className="cursor-pointer">
                      {isUploading ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Upload className="h-4 w-4 mr-2" />
                          Choose Files
                        </>
                      )}
                    </label>
                  </Button>
                </div>
                
                {uploadError && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg animate-fade-in">
                    <p className="text-sm text-red-600">{uploadError}</p>
                  </div>
                )}

                {uploadedFiles.length > 0 ? (
                  <div className="space-y-2">
                    <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Uploaded Files</p>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {uploadedFiles.map((file, index) => (
                        <div 
                          key={index} 
                          className="flex items-center gap-3 p-2.5 bg-gray-50 rounded-lg border border-gray-100 hover:bg-gray-100 transition-colors animate-fade-in"
                        >
                          <span className="text-lg">{getFileIcon(file)}</span>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-700 truncate">{file}</p>
                          </div>
                          <Badge variant="secondary" className="text-xs bg-green-50 text-green-700 border-green-200">
                            Ready
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <File className="h-10 w-10 mx-auto text-gray-300 mb-2" />
                    <p className="text-sm text-gray-400">No documents uploaded yet</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Query Section - Main Area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Query Input */}
            <Card className="shadow-sm border-gray-200 bg-white">
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div className="flex gap-3">
                    <Input
                      placeholder="Ask anything about your documents..."
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                      disabled={isSearching || uploadedFiles.length === 0}
                      className="h-12 text-base border-gray-200 focus:border-blue-500 focus:ring-blue-500"
                    />
                    <Button 
                      onClick={handleSearch} 
                      disabled={!query.trim() || isSearching || uploadedFiles.length === 0}
                      className="h-12 px-6 bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      {isSearching ? (
                        <Loader2 className="h-5 w-5 animate-spin" />
                      ) : (
                        <Search className="h-5 w-5" />
                      )}
                    </Button>
                  </div>
                  
                  {uploadedFiles.length === 0 && (
                    <p className="text-sm text-gray-400 text-center">Upload documents first to start querying</p>
                  )}
                </div>
              </CardContent>
            </Card>


            {isSearching && (
              <Card className="shadow-sm border-gray-200 bg-white animate-fade-in">
                <CardContent className="p-6">
                  <div className="space-y-3">
                    <Skeleton className="h-4 w-full bg-gray-200" />
                    <Skeleton className="h-4 w-5/6 bg-gray-200" />
                    <Skeleton className="h-4 w-4/6 bg-gray-200" />
                  </div>
                </CardContent>
              </Card>
            )}


            {searchError && (
              <Card className="shadow-sm border-red-200 bg-red-50 animate-fade-in">
                <CardContent className="p-4">
                  <p className="text-sm text-red-600">{searchError}</p>
                </CardContent>
              </Card>
            )}


            {answer && !isSearching && (
              <div className="space-y-4 animate-fade-in">
                <Card className="shadow-sm border-gray-200 bg-white">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base font-medium flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        Answer
                      </div>
                      {sources.length > 0 && (
                        <Badge 
                          variant="secondary" 
                          className={`text-xs ${
                            sources[0]?.score > 0.8 
                              ? 'bg-green-50 text-green-700 border-green-200' 
                              : sources[0]?.score > 0.6 
                              ? 'bg-yellow-50 text-yellow-700 border-yellow-200'
                              : 'bg-red-50 text-red-700 border-red-200'
                          }`}
                        >
                          {sources[0]?.score > 0.8 ? 'High' : sources[0]?.score > 0.6 ? 'Medium' : 'Low'} Confidence
                        </Badge>
                      )}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{answer}</p>
                    {sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <p className="text-xs text-gray-500">
                          Confidence based on {sources.length} source{sources.length > 1 ? 's' : ''} with {sources[0]?.score > 0.8 ? 'high' : sources[0]?.score > 0.6 ? 'medium' : 'low'} relevance
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
                

                {sources.length > 0 && (
                  <Card className="shadow-sm border-gray-200 bg-white">
                    <CardHeader 
                      className="pb-3 cursor-pointer hover:bg-gray-50 transition-colors"
                      onClick={() => setShowSources(!showSources)}
                    >
                      <CardTitle className="text-sm font-medium flex items-center justify-between">
                        <span className="text-gray-600">Sources ({sources.length})</span>
                        {showSources ? (
                          <ChevronUp className="h-4 w-4 text-gray-400" />
                        ) : (
                          <ChevronDown className="h-4 w-4 text-gray-400" />
                        )}
                      </CardTitle>
                    </CardHeader>
                    {showSources && (
                      <CardContent className="pt-0 space-y-3">
                        {sources.map((source, index) => (
                          <div 
                            key={index} 
                            className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors bg-gray-50/50"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <Badge variant="outline" className="text-xs font-normal bg-white">
                                  Source {index + 1}
                                </Badge>
                                {source.source_filename && (
                                  <span className="text-xs text-gray-500">
                                    {source.source_filename}
                                  </span>
                                )}
                              </div>
                              <Badge 
                                variant="secondary" 
                                className={`text-xs ${
                                  source.score > 0.8 
                                    ? 'bg-green-50 text-green-700 border-green-200' 
                                    : source.score > 0.6 
                                    ? 'bg-yellow-50 text-yellow-700 border-yellow-200'
                                    : 'bg-red-50 text-red-700 border-red-200'
                                }`}
                              >
                                {(source.score * 100).toFixed(0)}% match
                              </Badge>
                            </div>
                            <p className="text-sm text-gray-600 leading-relaxed">{source.content}</p>
                          </div>
                        ))}
                      </CardContent>
                    )}
                  </Card>
                )}
              </div>
            )}

            {/* Empty State */}
            {!answer && !isSearching && !searchError && uploadedFiles.length > 0 && (
              <Card className="shadow-sm border-gray-200 bg-gray-50/50">
                <CardContent className="p-12 text-center">
                  <div className="mx-auto w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4">
                    <Search className="h-8 w-8 text-blue-400" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to answer your questions</h3>
                  <p className="text-sm text-gray-500">Type your question above and press Enter or click the search button</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
