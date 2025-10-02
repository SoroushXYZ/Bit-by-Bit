import React from 'react';
import BaseGridComponent from './BaseGridComponent';
import { GitRepoComponent as GitRepoComponentType } from '@/types/components';

interface Props {
  component: GitRepoComponentType;
}

export default function GitRepoComponent({ component }: Props) {
  const { name, stars, description } = component;

  const formatStars = (count: number) => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toString();
  };

  return (
    <BaseGridComponent
      component={component}
      className="bg-gray-50 border-gray-200 hover:border-gray-300"
    >
      <div className="h-full flex flex-col text-center">
        {/* GitHub icon and repo name */}
        <div className="flex items-center justify-center mb-1">
          <img 
            src="/icons/github.svg" 
            alt="GitHub" 
            className="w-4 h-4 mr-2 flex-shrink-0"
          />
          <h3 className="text-xs font-bold text-gray-800 line-clamp-2 text-left break-words">
            {name}
          </h3>
        </div>

        {/* Stars */}
        <div className="flex items-center justify-center text-xs text-gray-600 mb-2">
          <span className="mr-1">⭐</span>
          <span>{formatStars(stars)}</span>
        </div>

        {/* Description */}
        <p className="text-xs text-muted-foreground flex-1 break-words overflow-hidden">
          {description}
        </p>
      </div>
    </BaseGridComponent>
  );
}
