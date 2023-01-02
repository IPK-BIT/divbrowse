<script>
export let size = 'normal';
</script>


<div class="loader" class:small="{size === 'small'}" class:tiny="{size === 'tiny'}" class:large="{size === 'large'}" ><!--<div class="loader2"></div>--></div>


<style>
.loader {
    border: 6px solid rgb(220,220,220);
    border-top: 6px solid #000;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}

.small {
    width: 20px;
    height: 20px;
    border: 4px solid rgb(220,220,220);
    border-top: 4px solid #000;
}

.tiny {
    width: 10px;
    height: 10px;
    border: 2px solid rgb(220,220,220);
    border-top: 2px solid #000;
}

.large {
    width: 60px;
    height: 60px;
    border: 8px solid rgb(220,220,220);
    border-top: 8px solid #000;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/*
.loader2 {
  display: inline-block;
  width: 80px;
  height: 80px;
}
.loader2:after {
  content: " ";
  display: block;
  width: 64px;
  height: 64px;
  margin: 8px;
  border-radius: 50%;
  border: 6px solid #000;
  border-color: #000 transparent #000 transparent;
  animation: loader2 1.2s linear infinite;
}
@keyframes loader2 {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
*/
</style>