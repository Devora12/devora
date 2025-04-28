export default function Loader() {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="flex space-x-1">
          <div className="w-2 h-8 bg-blue-500 animate-wave" />
          <div className="w-2 h-8 bg-blue-500 animate-wave [animation-delay:0.1s]" />
          <div className="w-2 h-8 bg-blue-500 animate-wave [animation-delay:0.2s]" />
          <div className="w-2 h-8 bg-blue-500 animate-wave [animation-delay:0.3s]" />
          <div className="w-2 h-8 bg-blue-500 animate-wave [animation-delay:0.4s]" />
        </div>
      </div>
    );
  }
  