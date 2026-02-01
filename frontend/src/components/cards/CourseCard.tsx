import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface CourseCardProps {
  title: string;
  category: string;
  image: string;
  description?: string;
  progress?: number;
  isStarted?: boolean;
}

export function CourseCard({
  title,
  category,
  image,
  description,
  progress,
  isStarted = false,
}: CourseCardProps) {
  return (
    <div className="bg-card rounded-2xl shadow-sm border border-border overflow-hidden group">
      <div
        className="h-32 bg-secondary bg-cover bg-center"
        style={{ backgroundImage: `url('${image}')` }}
      />
      <div className="p-6">
        <span className="text-primary font-bold text-[10px] uppercase tracking-wider">
          {category}
        </span>
        <h5 className="font-bold text-lg mt-1 group-hover:text-primary transition-colors">
          {title}
        </h5>

        {isStarted && progress !== undefined ? (
          <>
            <div className="flex items-center gap-2 mt-4">
              <Progress value={progress} className="flex-1 h-1.5" />
              <span className="text-xs font-semibold text-muted-foreground">{progress}%</span>
            </div>
            <Button variant="outline" className="w-full mt-6 font-bold border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground">
              Resume Learning
            </Button>
          </>
        ) : (
          <>
            {description && (
              <p className="text-muted-foreground text-sm mt-3 line-clamp-2">{description}</p>
            )}
            <Button className="w-full mt-6 font-bold">Start Course</Button>
          </>
        )}
      </div>
    </div>
  );
}
