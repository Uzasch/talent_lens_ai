import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

function DropZone({ onFilesAdded }) {
  const { toast } = useToast();

  const onDrop = useCallback(
    (acceptedFiles, rejectedFiles) => {
      if (rejectedFiles.length > 0) {
        toast({
          variant: 'destructive',
          title: 'Invalid file type',
          description: 'Only PDF files are accepted',
        });
      }
      if (acceptedFiles.length > 0) {
        onFilesAdded(acceptedFiles);
      }
    },
    [onFilesAdded, toast]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    multiple: true,
  });

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-8
        flex flex-col items-center justify-center
        cursor-pointer transition-colors
        ${
          isDragActive
            ? 'border-primary bg-primary/10'
            : 'border-border hover:border-muted-foreground'
        }
      `}
    >
      <input {...getInputProps()} />
      <Upload
        className={`h-10 w-10 mb-4 ${isDragActive ? 'text-primary' : 'text-muted-foreground'}`}
      />
      <p className="text-center">
        <span className="font-medium">Drop resumes here</span>
        <br />
        <span className="text-sm text-muted-foreground">or click to browse • PDF only</span>
      </p>
    </div>
  );
}

export default DropZone;
