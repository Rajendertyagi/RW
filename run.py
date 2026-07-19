import sys
import multiprocessing
if __name__ == '__main__':
    # Support for multiprocessing when frozen
    multiprocessing.freeze_support()
    
    # Import and run the Repowise CLI
    try:
        from repowise.cli import main
        sys.exit(main())
    except Exception as e:
        print(f"Error starting Repowise: {e}", file=sys.stderr)
        sys.exit(1)
