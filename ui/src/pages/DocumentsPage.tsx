import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Upload, File, Trash2, Loader2, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { documentsApi, type Document } from "@/api/documents";

function DeleteDialog({
  doc,
  onConfirm,
  isPending,
}: {
  doc: Document;
  onConfirm: () => void;
  isPending: boolean;
}) {
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <Trash2 className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete Manual</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete "{doc.original_filename}"? This
            action cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="destructive"
            disabled={isPending}
            onClick={() => {
              onConfirm();
              setOpen(false);
            }}
          >
            {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export function DocumentsPage() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ["documents"],
    queryFn: documentsApi.getDocuments,
  });

  const uploadMutation = useMutation({
    mutationFn: documentsApi.uploadDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      if (fileInputRef.current) fileInputRef.current.value = "";
    },
  });

  const deleteMutation = useMutation({
    mutationFn: documentsApi.deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  const triggerUpload = () => fileInputRef.current?.click();

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div className="flex-1 overflow-auto p-6">
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Manuals</h1>
          {documents.length > 0 && (
            <Button onClick={triggerUpload} disabled={uploadMutation.isPending}>
              {uploadMutation.isPending ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Upload className="mr-2 h-4 w-4" />
              )}
              Upload Manual
            </Button>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.doc,.docx"
          onChange={handleFileUpload}
          className="hidden"
        />

        {uploadMutation.isPending && (
          <Card className="border-dashed">
            <CardContent className="flex items-center gap-4 py-6">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <div>
                <p className="font-medium">Uploading & processing manual...</p>
                <p className="text-sm text-muted-foreground">
                  This may take a moment while we extract text and generate
                  embeddings.
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : documents.length === 0 && !uploadMutation.isPending ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
                <File className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="mt-4 text-lg font-semibold">No manuals yet</h3>
              <p className="mt-1 text-sm text-muted-foreground text-center max-w-sm">
                Upload your first synthesizer manual to get started. Supported
                formats: PDF, TXT, DOC, DOCX.
              </p>
              <Button className="mt-4" onClick={triggerUpload}>
                <Upload className="mr-2 h-4 w-4" />
                Upload Manual
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="flex flex-col gap-2">
            {documents.map((doc) => (
              <Card key={doc.id} className="group">
                <CardContent className="flex items-center gap-4 p-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
                    <FileText className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">
                      {doc.original_filename}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(doc.file_size)} · {doc.num_pages} pages · {doc.num_chunks} chunks · {new Date(doc.upload_date).toLocaleDateString()}
                    </p>
                  </div>
                  <DeleteDialog
                    doc={doc}
                    onConfirm={() => deleteMutation.mutate(doc.id)}
                    isPending={deleteMutation.isPending}
                  />
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
